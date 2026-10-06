using UnrealBuildTool;

public class CampusCenterEditorTarget : TargetRules
{
	public CampusCenterEditorTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Editor;
		ExtraModuleNames.Add("CampusCenter");
	}
}
