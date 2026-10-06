using UnrealBuildTool;

public class CampusCenterClientTarget : TargetRules
{
	public CampusCenterClientTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Client;
		ExtraModuleNames.Add("CampusCenter");
	}
}
