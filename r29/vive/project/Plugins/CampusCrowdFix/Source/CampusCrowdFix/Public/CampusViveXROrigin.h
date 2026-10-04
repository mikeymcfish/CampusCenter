#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CampusViveXROrigin.generated.h"

// New R07 map only: the retained first-person camera already supplies eye elevation.
UCLASS(BlueprintType)
class CAMPUSCROWDFIX_API ACampusViveXROrigin : public AActor
{
 GENERATED_BODY()
public:
 ACampusViveXROrigin();
 virtual void BeginPlay() override;
 UPROPERTY(BlueprintReadOnly, Transient, Category="Vive XR") bool LocalOriginApplied = false;
 UFUNCTION(BlueprintCallable, Category="Vive XR|Diagnostic", meta=(DevelopmentOnly))
 bool DiagnosticInject(float Left, float Right);
 UFUNCTION(BlueprintPure, Category="Vive XR")
 bool ContextRegisteredForOpenXR() const;
};
