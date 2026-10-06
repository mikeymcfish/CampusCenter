#pragma once
#include "Subsystems/WorldSubsystem.h"
#include "CampusProjectorSender.generated.h"
class UOSCClient;

// Opt-in, transient telemetry only. Does not own a camera, input or scene actor.
UCLASS()
class CAMPUSCROWDFIX_API UCampusProjectorSender : public UTickableWorldSubsystem
{
 GENERATED_BODY()
public:
 virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
 virtual void Initialize(FSubsystemCollectionBase& Collection) override;
 virtual void Deinitialize() override;
 virtual void Tick(float DeltaTime) override;
 virtual TStatId GetStatId() const override;
 UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly, WorldContext="WorldContextObject"), Category="Campus Projector|Diagnostic")
 static FVector DiagnosticTraceSupport(UObject* WorldContextObject, FVector Start, FVector End);
 UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly), Category="Campus Projector|Diagnostic")
 void DiagnosticFocus(bool Focused);
private:
 UPROPERTY(Transient) TObjectPtr<UOSCClient> Client;
 FString Session;
 int32 Sequence = 0;
 int32 LastFloor = -1;
 double NextSend = 0;
 double LastSend = 0;
 FVector LastPosition = FVector::ZeroVector;
 bool LastValid = false;
 bool Recentered = true;
 FDelegateHandle RecenterHandle;
 bool QAFocusEnabled = false;
 bool QAFocused = false;
 void NewSession();
};
