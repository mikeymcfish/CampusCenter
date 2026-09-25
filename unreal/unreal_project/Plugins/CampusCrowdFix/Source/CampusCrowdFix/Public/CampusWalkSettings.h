#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CampusWalkSettings.generated.h"

UCLASS()
class CAMPUSCROWDFIX_API ACampusWalkSettings : public AActor
{
 GENERATED_BODY()
public:
 ACampusWalkSettings();
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Campus Walkthrough", meta=(ClampMin="50", Units="cm/s"))
 float WalkSpeed = 360.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Campus Walkthrough", meta=(ClampMin="50", Units="cm/s"))
 float RunSpeed = 600.f;
};
