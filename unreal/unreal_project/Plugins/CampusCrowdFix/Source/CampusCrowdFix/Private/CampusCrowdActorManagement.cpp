#include "CampusCrowdActorManagement.h"
#include "Modules/ModuleManager.h"
#include "Components/CapsuleComponent.h"
#include "MassCommandBuffer.h"
#include "MassCommonFragments.h"
#include "MassEntityManager.h"
#include "MassActorSpawnerSubsystem.h"
#include "MassRepresentationTypes.h"
#include "MoverComponent.h"
#include "DefaultMovementSet/InstantMovementEffects/BasicInstantMovementEffects.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, CampusCrowdFix)

namespace
{
 void SyncMover(AActor& Actor)
 {
  if (UMoverComponent* Mover = Actor.FindComponentByClass<UMoverComponent>())
  {
   TSharedPtr<FAsyncTeleportEffect> Effect = MakeShared<FAsyncTeleportEffect>();
   Effect->TargetLocation = Actor.GetActorLocation();
   Effect->bUseActorRotation = false;
   Effect->TargetRotation = Actor.GetActorRotation();
   Mover->QueueInstantMovementEffect(Effect);
  }
 }
}

void UCampusCrowdActorManagement::SetActorEnabled(EMassActorEnabledType Type, AActor& Actor, int32 EntityIdx, FMassCommandBuffer& Commands) const
{
 Super::SetActorEnabled(Type, Actor, EntityIdx, Commands);
 const bool Enabled = Type != EMassActorEnabledType::Disabled;
 // Match MetaHuman's multi-component visibility and tick handling.
 TInlineComponentArray<UActorComponent*> Components;
 Actor.GetComponents(Components);
 for (UActorComponent* Component : Components)
 {
  Component->RegisterAllComponentTickFunctions(Enabled && Component->PrimaryComponentTick.bStartWithTickEnabled);
  if (USceneComponent* Scene = Cast<USceneComponent>(Component))
   Scene->SetVisibility(Enabled && !Component->ComponentTags.Contains(FName("Hidden")));
 }
}

void UCampusCrowdActorManagement::TeleportActor(const FTransform& Transform, AActor& Actor, FMassCommandBuffer& Commands) const
{
 // Base queues the capsule-adjusted, ground-snapped actor transform. Read its
 // result AFTER that deferred command, never the old pooled actor position.
 Super::TeleportActor(Transform, Actor, Commands);
 TWeakObjectPtr<AActor> WeakActor(&Actor);
 Commands.PushCommand<FMassDeferredSetCommand>([WeakActor](FMassEntityManager&)
 {
  if (AActor* LiveActor = WeakActor.Get()) SyncMover(*LiveActor);
 });
}

EMassActorSpawnRequestAction UCampusCrowdActorManagement::OnPostActorSpawn(const FMassActorSpawnRequestHandle& Handle, FConstStructView Request, TSharedRef<FMassEntityManager> EntityManager) const
{
 const auto Result = Super::OnPostActorSpawn(Handle, Request, EntityManager);
 check(Request.GetScriptStruct() == FMassActorSpawnRequest::StaticStruct());
 const auto& Spawn = *reinterpret_cast<const FMassActorSpawnRequest*>(Request.GetMemory());
 if (AActor* Actor = Spawn.SpawnedActor)
 {
  // Blueprint-created capsules may not exist on the template CDO queried by
  // the base spawn path. Use the actual capsule and entity feet transform.
  const FTransformFragment* Feet = EntityManager->GetFragmentDataPtr<FTransformFragment>(Spawn.MassAgent);
  check(Feet);
  FTransform Root = Feet->GetTransform();
  if (const UCapsuleComponent* Capsule = Actor->FindComponentByClass<UCapsuleComponent>())
   Root.AddToTranslation(FVector(0, 0, Capsule->GetScaledCapsuleHalfHeight()));
  Actor->SetActorTransform(Root, false, nullptr, ETeleportType::TeleportPhysics);
  SyncMover(*Actor);
 }
 return Result;
}
