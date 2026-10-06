using UnrealBuildTool;
public class CampusCrowdFix : ModuleRules
{
 public CampusCrowdFix(ReadOnlyTargetRules Target) : base(Target)
 {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  if (Target.bBuildEditor) PrivateDependencyModuleNames.Add("UnrealEd");
  PrivateDependencyModuleNames.Add("OSC");
  PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "HeadMountedDisplay", "MassCrowd", "MassRepresentation", "MassEntity", "MassCommon", "MassCore", "MassActors", "MassSpawner", "Mover" });
 }
}
