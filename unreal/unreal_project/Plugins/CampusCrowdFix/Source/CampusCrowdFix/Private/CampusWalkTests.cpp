#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "CampusWalkSettings.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "Editor.h"

class FCheckCampusShift : public IAutomationLatentCommand
{
 FAutomationTestBase* Test;
 int Stage = 0;
 int Frames = 0;
 int WaitFrames = 0;
public:
 explicit FCheckCampusShift(FAutomationTestBase* InTest) : Test(InTest) {}
 bool Update() override
 {
  if (++Frames < 5) return false;
  Frames = 0;
  UWorld* World = nullptr;
  for (const FWorldContext& Context : GEngine->GetWorldContexts())
   if (Context.WorldType == EWorldType::PIE) World = Context.World();
  APlayerController* PC = World ? UGameplayStatics::GetPlayerController(World, 0) : nullptr;
  ACharacter* Player = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
  ACampusWalkSettings* Settings = nullptr;
  if (World) for (TActorIterator<ACampusWalkSettings> It(World); It; ++It) { Settings = *It; break; }
  if (!Player || !Settings) { if (++WaitFrames < 300) return false; Test->AddError(TEXT("CampusCenter_Dusk Play did not become ready.")); return true; }
  if (Stage == 0)
  {
   Test->TestEqual(TEXT("Walking uses saved speed"), Player->GetCharacterMovement()->MaxWalkSpeed, Settings->WalkSpeed);
   PC->InputKey(FInputKeyParams(EKeys::LeftShift, IE_Pressed, 1.0));
  }
  else if (Stage == 1)
  {
   Test->TestTrue(TEXT("Shift is held"), PC->IsInputKeyDown(EKeys::LeftShift));
   Test->TestEqual(TEXT("Held Shift runs"), Player->GetCharacterMovement()->MaxWalkSpeed, Settings->RunSpeed);
   PC->InputKey(FInputKeyParams(EKeys::LeftShift, IE_Released, 0.0));
  }
  else
  {
   Test->TestEqual(TEXT("Releasing Shift restores walk speed"), Player->GetCharacterMovement()->MaxWalkSpeed, Settings->WalkSpeed);
   GEditor->RequestEndPlayMap();
   return true;
  }
  ++Stage; return false;
 }
};
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCampusShiftTest, "Campus.Walk.HoldShift", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FCampusShiftTest::RunTest(const FString& Parameters)
{
 FRequestPlaySessionParams Session;
 GEditor->RequestPlaySession(Session);
 ADD_LATENT_AUTOMATION_COMMAND(FCheckCampusShift(this));
 return true;
}
#endif
