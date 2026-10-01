using UnrealBuildTool;
public class CampusCrowdFix : ModuleRules
{
 public CampusCrowdFix(ReadOnlyTargetRules Target) : base(Target)
 {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  if (Target.bBuildEditor) PrivateDependencyModuleNames.Add("UnrealEd");
  PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "MassCrowd", "MassRepresentation", "MassEntity", "MassCommon", "MassCore", "MassActors", "MassSpawner", "Mover" });
 }
}
