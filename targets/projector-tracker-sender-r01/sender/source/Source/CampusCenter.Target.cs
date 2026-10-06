using UnrealBuildTool;

public class CampusCenterTarget : TargetRules
{
	public CampusCenterTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Game;
		ExtraModuleNames.Add("CampusCenter");
	}
}
