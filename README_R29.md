# CampusCenter R29 desktop and Vive

R29 contains the finalized trophy cases and three-dimensional awards, Commons furnishings, trainer counter/sink corrections, reconstructed gym floor artwork and ten local display lights. Existing source settings, controls, required cooked assets, and earlier releases are preserved.

Fetch and pull **main** in GitHub Desktop, then run **Start_CampusCenter_Vive.cmd** or **Start_CampusCenter_Desktop.cmd**. The launcher verifies and downloads the pinned R29 build into `.cc/r29`; existing R28 caches remain untouched. Start SteamVR with the connected headset/controllers and select SteamVR as the active OpenXR runtime. Both builds use their tested default Windows bootstrap; standard rendering settings are unchanged.

The optional RTX 3050 launchers remain on [their separate branch](https://github.com/mikeymcfish/CampusCenter/tree/patch/vive-rtx3050-optional-20261004/optional-launchers/rtx3050). They are not automatically selected. Actual RTX 3050 headset freeze, low frame rate and controller issues reported on R28 remain unresolved; R29 is not hardware-certified.

Manual downloads: obtain every numbered part for your selected Windows ZIP, `ARCHIVE_MANIFEST.json` and `Reassemble-Downloads.ps1` from this release. Run the PowerShell joiner, extract the complete ZIP, and run `Windows/CampusCenter.exe`. Keep Engine and CampusCenter folders together. The manifests and SHA256SUMS pin exact bytes.

Editable sources: `CampusCenter_R29_Cumulative_Sources.zip` contains separate cumulative desktop/project and vive/project overlays, including their accepted R28 baseline and exact R29 native changes. Restore the appropriately licensed baseline using the [R28 instructions](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-r28-review-20261004), then overlay the corresponding platform project. Use UE 5.8 and preserve platform-specific configuration and CampusCrowdFix source. These overlays omit unredistributed Epic/MetaHuman/Fab/manufacturer dependencies and model weights.

Desktop map: `/Game/Campus/Maps/CampusCenter_FA26_Desktop_R29_TrophyTrainerGymCorrections`.
Vive map: `/Game/Campus/Maps/CampusCenter_Vive_R29_TrophyTrainerGymCorrections_r02`.

Both producer cook/package and normal launch/close validations passed. Vive software checks accounted for 2,992 actors and 2,143 game dependencies with none missing; 402 walking probes had no compared regressions, eight connected routes and 26 input plus five keyboard cases passed. These are software checks. Physical headset/controller operation, performance and slicing/print fit remain unverified. Inherited doorway/navigation constraints remain, including the Research doorway obstruction and constrained Lab corner/classroom edge approaches. The stair wall is retained; architectural finish/height interpretation remains unresolved.

Previously approved six graphic-only school-event poster textures retain attribution; redistribution rights remain unverified. User approval is not licensing evidence. Private raw photographs, student-name boards, credentials, personal files, debug symbols/logs, screenshots and private reports are excluded. Required tested cooked dependencies are retained intact. See provenance and end-user notices.
