#include "CampusViveXROrigin.h"
#include "Engine/Engine.h"
#include "IXRTrackingSystem.h"
#include "CampusViveTriggerWalk.h"
#include "EnhancedInputSubsystems.h"
#include "EnhancedInputDeveloperSettings.h"
#include "InputActionValue.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

ACampusViveXROrigin::ACampusViveXROrigin()
{
 PrimaryActorTick.bCanEverTick = false;
 SetActorEnableCollision(false);
}
bool ACampusViveXROrigin::DiagnosticInject(float Left, float Right)
{
#if !UE_BUILD_SHIPPING
 if (!FParse::Param(FCommandLine::Get(), TEXT("CampusViveInputQA"))) return false;
 APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
 ULocalPlayer* Player = PC ? PC->GetLocalPlayer() : nullptr;
 UEnhancedInputLocalPlayerSubsystem* Input = Player ? Player->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
 if (!Input) return false;
 for (TActorIterator<ACampusViveTriggerWalk> It(GetWorld()); It; ++It)
 {
  if (!It->LeftAction || !It->RightAction) return false;
  // Mirrors the installed OpenXRInput injection path, without simulating an XR session.
  Input->InjectInputForAction(It->LeftAction, FInputActionValue(FMath::Clamp(Left, 0.f, 1.f)), {}, {});
  Input->InjectInputForAction(It->RightAction, FInputActionValue(FMath::Clamp(Right, 0.f, 1.f)), {}, {});
  return true;
 }
#endif
 return false;
}
void ACampusViveXROrigin::BeginPlay()
{
 Super::BeginPlay();
 UE_LOG(LogTemp, Display, TEXT("CampusViveXR: trigger mapping registered before XR action creation=%s"), ContextRegisteredForOpenXR() ? TEXT("true") : TEXT("false"));
 if (GEngine && GEngine->XRSystem.IsValid() && GEngine->XRSystem->GetSystemName() == FName(TEXT("OpenXR")))
 {
  // Local eye-height reference avoids adding tracked floor height to the existing elevated camera.
  GEngine->XRSystem->SetTrackingOrigin(EHMDTrackingOrigin::Local);
  LocalOriginApplied = GEngine->XRSystem->GetTrackingOrigin() == EHMDTrackingOrigin::Local;
  UE_LOG(LogTemp, Display, TEXT("CampusViveXR: OpenXR local tracking origin applied=%s; existing pawn/camera/movement retained"), LocalOriginApplied ? TEXT("true") : TEXT("false"));
 }
 else UE_LOG(LogTemp, Warning, TEXT("CampusViveXR: no active OpenXR tracking provider; runtime and headset readiness unverified"));
}
bool ACampusViveXROrigin::ContextRegisteredForOpenXR() const
{
 const UEnhancedInputDeveloperSettings* Settings = GetDefault<UEnhancedInputDeveloperSettings>();
 if (!Settings || !Settings->bEnableDefaultMappingContexts) return false;
 for (const FDefaultContextSetting& Context : Settings->DefaultMappingContexts)
  if (Context.InputMappingContext.ToSoftObjectPath().ToString() == TEXT("/Game/Campus/ViveTriggerWalkR01/IMC_ViveTriggerWalk.IMC_ViveTriggerWalk") && Context.Priority == 0 && !Context.bAddImmediately) return true;
 return false;
}
