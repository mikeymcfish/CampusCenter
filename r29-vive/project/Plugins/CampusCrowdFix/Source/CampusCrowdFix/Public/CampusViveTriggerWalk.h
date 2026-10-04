#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CampusViveTriggerWalk.generated.h"

class UInputAction;
class UInputMappingContext;
class APlayerController;
class ACharacter;

// Added only to the versioned Vive map. Original pawns, mappings and speeds are untouched.
UCLASS(BlueprintType)
class CAMPUSCROWDFIX_API ACampusViveTriggerWalk : public AActor
{
 GENERATED_BODY()
public:
 ACampusViveTriggerWalk();
 virtual void Tick(float DeltaSeconds) override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Vive trigger walking") TObjectPtr<UInputMappingContext> MappingContext;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Vive trigger walking") TObjectPtr<UInputAction> LeftAction;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Vive trigger walking") TObjectPtr<UInputAction> RightAction;
 UPROPERTY(BlueprintReadOnly, Transient, Category="Vive trigger walking") bool Walking = false;
 UPROPERTY(BlueprintReadOnly, Transient, Category="Vive trigger walking") float LeftValue = 0;
 UPROPERTY(BlueprintReadOnly, Transient, Category="Vive trigger walking") float RightValue = 0;
 UPROPERTY(BlueprintReadOnly, Transient, Category="Vive trigger walking") float LastInputScale = 0;

 // Explicit development QA flag is required. Injects actual input keys, not teleport movement.
 UFUNCTION(BlueprintCallable, Category="Vive trigger walking|Diagnostic", meta=(DevelopmentOnly))
 bool DiagnosticFrame(float LeftAnalog, bool LeftClick, float RightAnalog, bool RightClick,
  bool Focused, bool LeftTracked, bool RightTracked, float WorldYaw);
 UFUNCTION(BlueprintCallable, Category="Vive trigger walking|Diagnostic", meta=(DevelopmentOnly))
 bool DiagnosticKey(FName Key, bool Pressed);
 UFUNCTION(BlueprintCallable, Category="Vive trigger walking|Diagnostic", meta=(DevelopmentOnly))
 void DiagnosticStop();
private:
 struct FHandState { bool Held = false; bool NeedsNeutral = true; };
 FHandState Hands[2];
 TWeakObjectPtr<APlayerController> BoundController;
 TWeakObjectPtr<ACharacter> BoundCharacter;
 bool BindController(APlayerController* PC);
 void UnbindController();
 bool UpdateHand(int32 Hand, float Value, bool Focused, bool Tracked);
 bool ControllerTracked(int32 Hand) const;
 bool FocusedAndHeadTracked() const;
 bool DiagnosticAllowed() const;
 bool Diagnostic = false;
 bool DiagnosticFocused = false;
 bool DiagnosticTracked[2] = {false, false};
 bool DiagnosticClicks[2] = {false, false};
 float DiagnosticYaw = 0;
};
