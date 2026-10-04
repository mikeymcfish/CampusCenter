#include "CampusViveTriggerWalk.h"
#include "EnhancedInputSubsystems.h"
#include "EnhancedPlayerInput.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputActionValue.h"
#include "InputKeyEventArgs.h"
#include "Engine/Engine.h"
#include "Engine/LocalPlayer.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
#include "Kismet/GameplayStatics.h"
#include "IXRTrackingSystem.h"
#include "IMotionController.h"
#include "Features/IModularFeatures.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"

ACampusViveTriggerWalk::ACampusViveTriggerWalk()
{
 PrimaryActorTick.bCanEverTick = true;
 PrimaryActorTick.TickGroup = TG_PrePhysics;
}
bool ACampusViveTriggerWalk::BindController(APlayerController* PC)
{
 if (BoundController.Get() == PC && BoundCharacter.Get() == Cast<ACharacter>(PC->GetPawn())) return true;
 UnbindController();
 ACharacter* Character = Cast<ACharacter>(PC->GetPawn());
 ULocalPlayer* Local = PC->GetLocalPlayer();
 UEnhancedInputLocalPlayerSubsystem* Subsystem = Local ? Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
 if (!Character || !Subsystem || !MappingContext || !LeftAction || !RightAction) return false;
 BoundController = PC; BoundCharacter = Character;
 Subsystem->AddMappingContext(MappingContext, 0);
 AddTickPrerequisiteActor(PC);
 Character->GetCharacterMovement()->AddTickPrerequisiteActor(this);
 Hands[0] = {}; Hands[1] = {};
 return true;
}
void ACampusViveTriggerWalk::UnbindController()
{
 if (ACharacter* Character = BoundCharacter.Get()) Character->GetCharacterMovement()->RemoveTickPrerequisiteActor(this);
 if (APlayerController* PC = BoundController.Get())
 {
  RemoveTickPrerequisiteActor(PC);
  if (ULocalPlayer* Local = PC->GetLocalPlayer())
   if (UEnhancedInputLocalPlayerSubsystem* Subsystem = Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
    if (MappingContext) Subsystem->RemoveMappingContext(MappingContext);
 }
 BoundController.Reset(); BoundCharacter.Reset(); Walking = false; LastInputScale = 0;
 Hands[0] = {}; Hands[1] = {};
}
void ACampusViveTriggerWalk::EndPlay(const EEndPlayReason::Type Reason)
{
 UnbindController(); Super::EndPlay(Reason);
}
bool ACampusViveTriggerWalk::UpdateHand(int32 Hand, float Value, bool Focused, bool Tracked)
{
 FHandState& State = Hands[Hand];
 if (!Focused || !Tracked) { State.Held = false; State.NeedsNeutral = true; return false; }
 if (Value <= 0.05f) { State.Held = false; State.NeedsNeutral = false; }
 else if (Value >= 0.1f && !State.NeedsNeutral) State.Held = true;
 return State.Held;
}
bool ACampusViveTriggerWalk::ControllerTracked(int32 Hand) const
{
 const APlayerController* PC = BoundController.Get();
 const ULocalPlayer* Local = PC ? PC->GetLocalPlayer() : nullptr;
 if (!Local) return false;
 for (IMotionController* Device : IModularFeatures::Get().GetModularFeatureImplementations<IMotionController>(IMotionController::GetModularFeatureName()))
  if (Device && Device->GetControllerTrackingStatus(Local->GetControllerId(), Hand == 0 ? IMotionController::LeftHandSourceId : IMotionController::RightHandSourceId) == ETrackingStatus::Tracked) return true;
 return false;
}
bool ACampusViveTriggerWalk::FocusedAndHeadTracked() const
{
 if (!GEngine || !GEngine->XRSystem.IsValid() || !GEngine->XRSystem->IsHeadTrackingAllowedForWorld(*GetWorld()) || !GEngine->XRSystem->IsTracking(IXRTrackingSystem::HMDDeviceId)) return false;
 if (FApp::UseVRFocus()) return FApp::HasVRFocus();
 return GEngine->GameViewport && GEngine->GameViewport->Viewport && GEngine->GameViewport->Viewport->HasFocus() && GEngine->GameViewport->Viewport->IsForegroundWindow();
}
void ACampusViveTriggerWalk::Tick(float DeltaSeconds)
{
 Super::Tick(DeltaSeconds);
 APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
 if (!PC || !PC->IsLocalController() || !BindController(PC)) { Walking = false; LastInputScale = 0; return; }
 UEnhancedPlayerInput* Input = Cast<UEnhancedPlayerInput>(PC->PlayerInput);
 ACharacter* Character = BoundCharacter.Get();
 if (!Input || !Character) return;
 LeftValue = FMath::Clamp(Input->GetActionValue(LeftAction).Get<float>(), 0.f, 1.f);
 RightValue = FMath::Clamp(Input->GetActionValue(RightAction).Get<float>(), 0.f, 1.f);
 const bool Focused = Diagnostic ? DiagnosticFocused : FocusedAndHeadTracked();
 const bool LeftHeld = UpdateHand(0, LeftValue, Focused, Diagnostic ? DiagnosticTracked[0] : ControllerTracked(0));
 const bool RightHeld = UpdateHand(1, RightValue, Focused, Diagnostic ? DiagnosticTracked[1] : ControllerTracked(1));
 const bool WasWalking = Walking;
 Walking = LeftHeld || RightHeld; LastInputScale = Walking ? 1.f : 0.f;
 if (Walking)
 {
  const float Yaw = Diagnostic ? DiagnosticYaw : (PC->PlayerCameraManager ? PC->PlayerCameraManager->GetCameraRotation().Yaw : PC->GetControlRotation().Yaw);
  Character->AddMovementInput(FRotator(0.f, Yaw, 0.f).Vector(), 1.f);
 }
 else if (WasWalking && Character->GetPendingMovementInputVector().IsNearlyZero())
 {
  // Immediate trigger stop, without cancelling other existing movement input.
  Character->GetCharacterMovement()->StopMovementImmediately();
 }
}
bool ACampusViveTriggerWalk::DiagnosticAllowed() const
{
#if !UE_BUILD_SHIPPING
 return FParse::Param(FCommandLine::Get(), TEXT("CampusViveInputQA"));
#else
 return false;
#endif
}
bool ACampusViveTriggerWalk::DiagnosticFrame(float LA, bool LC, float RA, bool RC, bool Focused, bool LT, bool RT, float Yaw)
{
 if (!DiagnosticAllowed()) return false;
 APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
 if (!PC || !BindController(PC)) return false;
 Diagnostic = true; DiagnosticFocused = Focused; DiagnosticTracked[0] = LT; DiagnosticTracked[1] = RT; DiagnosticYaw = Yaw;
 const FName AxisNames[2] = {TEXT("Vive_Left_Trigger_Axis"), TEXT("Vive_Right_Trigger_Axis")};
 const FName ClickNames[2] = {TEXT("Vive_Left_Trigger_Click"), TEXT("Vive_Right_Trigger_Click")};
 const float Values[2] = {LA, RA}; const bool Clicks[2] = {LC, RC};
 for (int32 Hand = 0; Hand < 2; ++Hand)
 {
  PC->InputKey(FInputKeyEventArgs::CreateSimulated(FKey(AxisNames[Hand]), IE_Axis, FMath::Clamp(Values[Hand], 0.f, 1.f)));
  if (Clicks[Hand] != DiagnosticClicks[Hand]) PC->InputKey(FInputKeyEventArgs::CreateSimulated(FKey(ClickNames[Hand]), Clicks[Hand] ? IE_Pressed : IE_Released, Clicks[Hand] ? 1.f : 0.f));
  DiagnosticClicks[Hand] = Clicks[Hand];
 }
 return true;
}
bool ACampusViveTriggerWalk::DiagnosticKey(FName Key, bool Pressed)
{
 if (!DiagnosticAllowed()) return false;
 if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0)) return PC->InputKey(FInputKeyEventArgs::CreateSimulated(FKey(Key), Pressed ? IE_Pressed : IE_Released, Pressed ? 1.f : 0.f));
 return false;
}
void ACampusViveTriggerWalk::DiagnosticStop()
{
 if (!DiagnosticAllowed()) return;
 DiagnosticFrame(0, false, 0, false, false, false, false, 0); Diagnostic = false;
 Hands[0] = {}; Hands[1] = {};
}
