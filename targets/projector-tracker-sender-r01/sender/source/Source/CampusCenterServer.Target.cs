using UnrealBuildTool;

public class CampusCenterServerTarget : TargetRules
{
	public CampusCenterServerTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Server;
		ExtraModuleNames.Add("CampusCenter");
	}
}
