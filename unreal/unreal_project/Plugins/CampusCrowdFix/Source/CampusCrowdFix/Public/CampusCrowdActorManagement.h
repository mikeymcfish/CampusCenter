#pragma once
#include "CoreMinimal.h"
#include "MassCrowdRepresentationActorManagement.h"
#include "CampusCrowdActorManagement.generated.h"

UCLASS()
class CAMPUSCROWDFIX_API UCampusCrowdActorManagement : public UMassCrowdRepresentationActorManagement
{
 GENERATED_BODY()
public:
 virtual void SetActorEnabled(EMassActorEnabledType EnabledType, AActor& Actor, int32 EntityIdx, FMassCommandBuffer& CommandBuffer) const override;
 virtual void TeleportActor(const FTransform& Transform, AActor& Actor, FMassCommandBuffer& CommandBuffer) const override;
 virtual EMassActorSpawnRequestAction OnPostActorSpawn(const FMassActorSpawnRequestHandle& Handle, FConstStructView Request, TSharedRef<FMassEntityManager> EntityManager) const override;
};
