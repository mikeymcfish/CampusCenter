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
#include "UObject/ConstructorHelpers.h"

ACampusViveTriggerWalk::ACampusViveTriggerWalk()
{
 PrimaryActorTick.bCanEverTick = true;
 PrimaryActorTick.TickGroup = TG_PrePhysics;
 static ConstructorHelpers::FObjectFinder<UInputAction> LG(TEXT("/Game/Campus/ViveGripTurnR01/IA_GripTurn_Left.IA_GripTurn_Left"));
 static ConstructorHelpers::FObjectFinder<UInputAction> RG(TEXT("/Game/Campus/ViveGripTurnR01/IA_GripTurn_Right.IA_GripTurn_Right"));
 LeftGripAction = LG.Object; RightGripAction = RG.Object;
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
 if (FParse::Param(FCommandLine::Get(), TEXT("CampusViveControlLog"))) UE_LOG(LogTemp, Display, TEXT("CampusViveControl: bound input=%s gripActions=%s/%s"), PC->PlayerInput ? *PC->PlayerInput->GetClass()->GetName() : TEXT("none"), LeftGripAction ? *LeftGripAction->GetName() : TEXT("none"), RightGripAction ? *RightGripAction->GetName() : TEXT("none"));
 AddTickPrerequisiteActor(PC);
 Character->GetCharacterMovement()->AddTickPrerequisiteActor(this);
 Hands[0] = {}; Hands[1] = {};
 GripNeedsNeutral[0] = GripNeedsNeutral[1] = true;
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
 GripNeedsNeutral[0] = GripNeedsNeutral[1] = true;
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
 LeftGripValue = LeftGripAction ? FMath::Clamp(Input->GetActionValue(LeftGripAction).Get<float>(), 0.f, 1.f) : 0.f;
 RightGripValue = RightGripAction ? FMath::Clamp(Input->GetActionValue(RightGripAction).Get<float>(), 0.f, 1.f) : 0.f;
 const bool LT = Diagnostic ? DiagnosticTracked[0] : ControllerTracked(0);
 const bool RT = Diagnostic ? DiagnosticTracked[1] : ControllerTracked(1);
 const int32 InputMask = (LeftValue >= .1f ? 1 : 0) | (RightValue >= .1f ? 2 : 0) | (LeftGripValue >= .1f ? 4 : 0) | (RightGripValue >= .1f ? 8 : 0);
 const int32 TrackingMask = (LT ? 1 : 0) | (RT ? 2 : 0);
 if (!ControlStateLogged || Focused != LastControlFocus || InputMask != LastControlInputMask || TrackingMask != LastControlTrackingMask)
 { LogControlState(TEXT("focus/input/tracking-edge"), Focused, LT, RT); ControlStateLogged = true; LastControlFocus = Focused; LastControlInputMask = InputMask; LastControlTrackingMask = TrackingMask; }
 ProcessGripTurn(Focused, LT, RT);
 const bool LeftHeld = UpdateHand(0, LeftValue, Focused, Diagnostic ? DiagnosticTracked[0] : ControllerTracked(0));
 const bool RightHeld = UpdateHand(1, RightValue, Focused, Diagnostic ? DiagnosticTracked[1] : ControllerTracked(1));
 const bool WasWalking = Walking;
 Walking = LeftHeld || RightHeld; LastInputScale = Walking ? 1.f : 0.f;
 if (Walking)
 {
  const float Yaw = (Diagnostic ? DiagnosticYaw : (PC->PlayerCameraManager ? PC->PlayerCameraManager->GetCameraRotation().Yaw : PC->GetControlRotation().Yaw)) + GripDeltaThisFrame;
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
 GripNeedsNeutral[0] = GripNeedsNeutral[1] = true;
}

void ACampusViveTriggerWalk::LogControlState(const TCHAR* Event, bool Focused, bool LT, bool RT) const
{
 if (!FParse::Param(FCommandLine::Get(), TEXT("CampusViveControlLog"))) return;
 const APlayerController* PC = BoundController.Get(); const ACharacter* C = BoundCharacter.Get();
 FQuat Q; FVector P; bool Pose = GEngine && GEngine->XRSystem.IsValid() && GEngine->XRSystem->GetCurrentPose(IXRTrackingSystem::HMDDeviceId, Q, P);
 UE_LOG(LogTemp, Display, TEXT("CampusViveControl: event=%s focus=%d tracked=%d/%d trigger=%.3f/%.3f grip=%.3f/%.3f pawnYaw=%.2f controlYaw=%.2f cameraYaw=%.2f hmdYaw=%.2f origin=%d"), Event, Focused, LT, RT, LeftValue, RightValue, LeftGripValue, RightGripValue, C ? C->GetActorRotation().Yaw : 0.f, PC ? PC->GetControlRotation().Yaw : 0.f, PC && PC->PlayerCameraManager ? PC->PlayerCameraManager->GetCameraRotation().Yaw : 0.f, Pose ? Q.Rotator().Yaw : 0.f, GEngine && GEngine->XRSystem.IsValid() ? int32(GEngine->XRSystem->GetTrackingOrigin()) : -1);
}
void ACampusViveTriggerWalk::ProcessGripTurn(bool Focused, bool LT, bool RT)
{
 GripDeltaThisFrame = 0;
 const float V[2] = {LeftGripValue, RightGripValue}; const bool Tracked[2] = {LT, RT};
 if (!Focused) { GripNeedsNeutral[0] = GripNeedsNeutral[1] = true; return; }
 if (V[0] >= .1f && V[1] >= .1f) { GripNeedsNeutral[0] = GripNeedsNeutral[1] = true; return; }
 for (int32 Hand = 0; Hand < 2; ++Hand)
 {
  if (!Tracked[Hand]) { GripNeedsNeutral[Hand] = true; continue; }
  if (V[Hand] <= .05f) { GripNeedsNeutral[Hand] = false; continue; }
  if (V[Hand] >= .1f && !GripNeedsNeutral[Hand])
  {
   GripNeedsNeutral[Hand] = true; const float Degrees = Hand == 0 ? -30.f : 30.f;
   const bool Turned = SnapTurn(Degrees);
   LogControlState(Turned ? (Hand == 0 ? TEXT("snap-left") : TEXT("snap-right")) : TEXT("snap-blocked"), Focused, LT, RT);
  }
 }
}
bool ACampusViveTriggerWalk::SnapTurn(float Degrees)
{
 APlayerController* PC = BoundController.Get(); ACharacter* C = BoundCharacter.Get();
 if (!PC || !C || !PC->PlayerCameraManager) return false;
 const FVector Old = C->GetActorLocation(); FVector Pivot = PC->PlayerCameraManager->GetCameraLocation(); Pivot.Z = Old.Z;
 const FVector Next = Pivot + (Old - Pivot).RotateAngleAxis(Degrees, FVector::UpVector);
 FHitResult Hit; C->SetActorLocation(Next, true, &Hit, ETeleportType::None);
 if (Hit.bBlockingHit || !C->GetActorLocation().Equals(Next, .1f)) { C->SetActorLocation(Old, false, nullptr, ETeleportType::TeleportPhysics); return false; }
 FRotator Control = PC->GetControlRotation(); Control.Yaw = FRotator::NormalizeAxis(Control.Yaw + Degrees); PC->SetControlRotation(Control);
 FRotator Body = C->GetActorRotation(); Body.Yaw = FRotator::NormalizeAxis(Body.Yaw + Degrees); C->SetActorRotation(Body, ETeleportType::None);
 ++GripTurnCount; LastGripTurnDegrees = Degrees; GripDeltaThisFrame = Degrees; return true;
}
bool ACampusViveTriggerWalk::DiagnosticGrips(bool Left, bool Right)
{
 if (!DiagnosticAllowed()) return false;
 APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0); if (!PC || !BindController(PC)) return false;
 const bool Values[2] = {Left, Right}; const FName Keys[2] = {TEXT("Vive_Left_Grip_Click"), TEXT("Vive_Right_Grip_Click")};
 for (int32 Hand = 0; Hand < 2; ++Hand)
 {
  if (Values[Hand] != DiagnosticGripClicks[Hand]) PC->InputKey(FInputKeyEventArgs::CreateSimulated(FKey(Keys[Hand]), Values[Hand] ? IE_Pressed : IE_Released, Values[Hand] ? 1.f : 0.f));
  DiagnosticGripClicks[Hand] = Values[Hand];
 }
 return true;
}
