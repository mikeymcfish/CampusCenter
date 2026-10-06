#include "CampusProjectorSender.h"
#include "OSCClient.h"
#include "OSCManager.h"
#include "OSCMessage.h"
#include "Camera/PlayerCameraManager.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "IXRTrackingSystem.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/CoreDelegates.h"
#include "Misc/DateTime.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"
#include "Engine/World.h"

void UCampusProjectorSender::DiagnosticFocus(bool Focused)
{
#if !UE_BUILD_SHIPPING
 if (FParse::Param(FCommandLine::Get(), TEXT("CampusProjectorQA")))
 { QAFocusEnabled = true; QAFocused = Focused; }
#endif
}

FVector UCampusProjectorSender::DiagnosticTraceSupport(UObject* WorldContextObject, FVector Start, FVector End)
{
#if !UE_BUILD_SHIPPING
 if (FParse::Param(FCommandLine::Get(), TEXT("CampusProjectorQA")) && GEngine)
 {
  UWorld* World = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::ReturnNull);
  FHitResult Hit;
  FCollisionQueryParams Params(SCENE_QUERY_STAT(CampusProjectorFloorAudit), true);
  if (World && World->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params)
   && Hit.ImpactNormal.Z >= 0.7) return Hit.ImpactPoint;
 }
#endif
 return FVector(0,0,-99999);
}

bool UCampusProjectorSender::ShouldCreateSubsystem(UObject* Outer) const
{
 const UWorld* World = Cast<UWorld>(Outer);
 return World && (World->WorldType == EWorldType::Game || World->WorldType == EWorldType::PIE)
  && FParse::Param(FCommandLine::Get(), TEXT("CampusProjector"));
}
void UCampusProjectorSender::NewSession()
{
 Session = TEXT("ue-") + FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphensLower);
 Sequence = 0; Recentered = true; LastValid = false; LastFloor = -1;
}
void UCampusProjectorSender::Initialize(FSubsystemCollectionBase& Collection)
{
 Super::Initialize(Collection);
 NewSession();
 Client = UOSCManager::CreateOSCClient(TEXT("127.0.0.1"), 9001, TEXT("CampusProjectorLoopbackV1"), this);
 RecenterHandle = FCoreDelegates::VRHeadsetRecenter.AddLambda([this]() { Recentered = true; });
 UE_LOG(LogTemp, Display, TEXT("CampusProjector: opt-in OSC v1 loopback 127.0.0.1:9001, max 20Hz, session=%s"), *Session);
}
void UCampusProjectorSender::Deinitialize()
{
 FCoreDelegates::VRHeadsetRecenter.Remove(RecenterHandle);
 Client = nullptr;
 Super::Deinitialize();
}
TStatId UCampusProjectorSender::GetStatId() const
{
 RETURN_QUICK_DECLARE_CYCLE_STAT(UCampusProjectorSender, STATGROUP_Tickables);
}
void UCampusProjectorSender::Tick(float DeltaTime)
{
 Super::Tick(DeltaTime);
 const double Now = FPlatformTime::Seconds();
 if (!Client || Now < NextSend) return;
 // Keep the nominal 20Hz cadence across frame quantization; discard missed periods.
 // At most one message per game tick, with no catch-up loop after a stall.
 NextSend = Now - NextSend >= 0.05 ? Now + 0.05 : NextSend + 0.05;
 if (Sequence == MAX_int32) NewSession();
 APlayerController* PC = UGameplayStatics::GetPlayerController(GetWorld(), 0);
 ACharacter* Character = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
 APlayerCameraManager* Camera = PC ? PC->PlayerCameraManager : nullptr;
 FVector Position = Camera ? Camera->GetCameraLocation() : FVector::ZeroVector;
 float Yaw = Camera ? Camera->GetCameraRotation().Yaw : 0.f;
 const bool Finite = !Position.ContainsNaN() && FMath::IsFinite(Yaw);
 if (!Finite) { Position = FVector::ZeroVector; Yaw = 0.f; }
 bool Focused = GEngine && GEngine->GameViewport && GEngine->GameViewport->Viewport
  && GEngine->GameViewport->Viewport->HasFocus() && GEngine->GameViewport->Viewport->IsForegroundWindow();
 const bool VRRequested = FParse::Param(FCommandLine::Get(), TEXT("vr"));
 const bool XRActive = GEngine && GEngine->XRSystem.IsValid()
  && GEngine->XRSystem->IsHeadTrackingAllowedForWorld(*GetWorld());
 bool Tracked = !VRRequested;
 if (XRActive)
 {
  Tracked = GEngine->XRSystem->IsTracking(IXRTrackingSystem::HMDDeviceId);
  if (FApp::UseVRFocus()) Focused = FApp::HasVRFocus();
 }
#if !UE_BUILD_SHIPPING
 if (QAFocusEnabled) Focused = QAFocused; // Controlled desktop PIE QA only; never fakes XR tracking.
#endif
 int32 Floor = -1;
 UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
 if (Movement && Movement->IsMovingOnGround() && Movement->CurrentFloor.IsWalkableFloor())
 {
  // Support height is independent of HMD eye height (including the tall ground-floor gym).
  const double Z = Movement->CurrentFloor.HitResult.ImpactPoint.Z;
  if (FMath::IsFinite(Z) && Z >= -40.0 && Z <= 486.72)
  {
   // Verified R29 support levels; 40 cm hysteresis prevents stair midpoint chatter.
   constexpr double Midpoint = 213.36; // Ground 0, upper finished datum 426.72 cm.
   Floor = LastFloor == 0 ? (Z > Midpoint + 40.0 ? 1 : 0)
    : LastFloor == 1 ? (Z < Midpoint - 40.0 ? 0 : 1) : (Z > Midpoint ? 1 : 0);
   LastFloor = Floor;
  }
 }
 const bool Valid = Camera && Character && Finite && Focused && Tracked && Floor >= 0;
 if (!Valid) Floor = -1;
 const double Gap = LastSend > 0 ? Now - LastSend : 0;
 const bool Jump = LastValid && Valid && ((Position - LastPosition).Size() > 100.0 || Gap > 0.5);
 const bool Teleport = Sequence == 0 || Recentered || (Valid && !LastValid) || Jump;
 FOSCMessage Message;
 Message.SetAddress(FOSCAddress(TEXT("/campuscenter/player/v1")));
 UOSCManager::AddInt32(Message, 1);
 UOSCManager::AddString(Message, TEXT("campuscenter-r29-p02-sample-1-250-v1"));
 UOSCManager::AddString(Message, Session);
 UOSCManager::AddInt32(Message, Sequence++);
 const FDateTime UTC = FDateTime::UtcNow();
 UOSCManager::AddString(Message, LexToString((UTC.GetTicks() - FDateTime(1970,1,1).GetTicks()) / ETimespan::TicksPerMillisecond));
 UOSCManager::AddFloat(Message, static_cast<float>(Position.X));
 UOSCManager::AddFloat(Message, static_cast<float>(Position.Y));
 UOSCManager::AddFloat(Message, static_cast<float>((Position.X + 4700.0) / 25.0));
 UOSCManager::AddFloat(Message, static_cast<float>((-Position.Y + 230.0) / 25.0));
 UOSCManager::AddFloat(Message, Yaw);
 UOSCManager::AddInt32(Message, Floor);
 UOSCManager::AddInt32(Message, Valid ? 1 : 0);
 UOSCManager::AddInt32(Message, Teleport ? 1 : 0);
 Client->SendOSCMessage(Message);
 LastPosition = Position; LastValid = Valid; LastSend = Now; Recentered = false;
}
