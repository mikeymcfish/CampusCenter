#include "CampusWalkSettings.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"

ACampusWalkSettings::ACampusWalkSettings()
{
 PrimaryActorTick.bCanEverTick = true;
 PrimaryActorTick.TickGroup = TG_PrePhysics;
}
void ACampusWalkSettings::Tick(float DeltaSeconds)
{
 Super::Tick(DeltaSeconds);
 APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
 if (!PC || !PC->IsLocalController()) return;
 if (ACharacter* Character = Cast<ACharacter>(PC->GetPawn()))
 {
  const bool Running = PC->IsInputKeyDown(EKeys::LeftShift) || PC->IsInputKeyDown(EKeys::RightShift);
  Character->GetCharacterMovement()->MaxWalkSpeed = Running ? FMath::Max(RunSpeed, WalkSpeed) : WalkSpeed;
 }
}
