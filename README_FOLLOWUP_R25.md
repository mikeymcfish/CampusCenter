# CampusCenter desktop R25 and Vive R07 OpenXR

This follow-up adds fourteen improved equipment assemblies, cleaned silver cup and regional plaque display assets, and a fictional static BSOD on reception TV65. The earlier v26 final release remains available and unchanged. The BSOD is decorative artwork, not an operating system error or slideshow.

Sources: [combined R25/R07 branch](https://github.com/mikeymcfish/CampusCenter/tree/release/combined-r25-trigger-20261001/followup-r25), [Vive branch preserving codex/vr ancestry](https://github.com/mikeymcfish/CampusCenter/tree/release/vive-trigger-forward-20261001/followup-vive). Licensed baseline reconstruction remains required; these are project-owned overlays.

## Downloads and desktop launch

Download every numbered `CampusCenter_Desktop_R25_Windows.zip.partNN` file, `ARCHIVE_MANIFEST.json` and `Reassemble-Downloads.ps1` into one folder. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\Reassemble-Downloads.ps1`. Extract the resulting ZIP completely, keeping `CampusCenter` and `Engine` beside `Windows/CampusCenter.exe`. Launch that EXE; its tested bootstrap opens R25 automatically.

The equipment ZIP contains editable Blender geometry, GLB exports, source scripts, dimensions and checks. `SilverCup_Ready.zip` and `RegionalPlaque_Ready.zip` contain editable Blender/FBX/GLB outputs, preview images and provenance. These are manually cleaned Trellis hybrids with blank plates, not authentic award replicas or fabrication unions. Model weights and rejected prototypes are excluded. Ready-package notes describe the asset-preparation stage; final integration and package review records are in `desktop-review`.

`CampusCenter_R25_Combined_Delta_R02.zip` contains 39 new Unreal assets and one new map, `/Game/Campus/Maps/CampusCenter_FA26_Desktop_R25_CombinedReview`. Apply it to the appropriately licensed editable desktop baseline documented in the [v26 final release](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-v26-final-20261001). This delta is not a standalone Unreal project. Do not overwrite previous maps. Third-party raw dependency exclusions and the packaged application's end-user notice remain in effect.

`CampusCenter_R25_R07_Final_Sources.zip` contains the combined project-owned source overlays, editable equipment/trophies, review gallery, scripts and manifests. For desktop, copy `desktop-delta/Content` into the restored prior editable desktop project. For Vive, restore the prior licensed editable Vive baseline and overlay `vive/project` into its project root, compile the supplied CampusCrowdFix source using the prior documented UE 5.8 toolchain, and open the R07 map. The dedicated Vive branch contains the same overlay under `followup-vive/project`. Exact original text bytes are preserved in the source ZIP; Git may normalize text line endings. Large model/map assets use Git LFS, which must be fetched when using Git checkout.

## Validation and limits

Desktop cook, packaging, default-launch smoke and saved native geometry/material checks passed. The two final trophy actors explicitly use NoCollision; original cases retain BlockAll. Sixteen distinct paired walking routes across the R22/R24 and final R25 records show no new regressions. Two inherited failures remain: Research113_25 and Fitness_RackFront_Aisle. Original approved case footprints and seven corrected bench donors are preserved. Scoped visual evidence is included; some fine contacts are dark or occluded.

Cold and warm launch observations include shader/PSO hitches and an audio-buffer underrun. Frame-rate performance is not certified. Equipment mechanics, heights and clearances are inferred, not manufacturer or architect certified. Actual headset/controller testing and physical slicing/print fit remain untested.

## Vive controls and package

**OpenXR-enabled Vive build; hardware/runtime acceptance untested.** On the intended Vive computer, SteamVR must be installed and selected as the active OpenXR runtime, with headset/controllers connected. No SteamVR installation or system runtime selection was performed during this work.

Download every `CampusCenter_Vive_R07_OpenXR_Windows.zip.partNN` into the same folder as `ARCHIVE_MANIFEST.json` and `Reassemble-Downloads.ps1`. Run the joining script, extract the ZIP completely, and run `Windows/Review_CampusCenter_Vive_R07_OpenXR.cmd`. This launcher selects `/Game/Campus/Maps/CampusCenter_Vive_EQ27_R07_OpenXR` and requests VR with `-vr`. The raw EXE retains the original default map and is not the R07 review entry point. Keep all extracted Engine and CampusCenter files together.

Hold either controller trigger to walk forward in the camera/headset's horizontal facing direction; release to stop trigger-only walking. Both trigger value and click bind through `/interaction_profiles/htc/vive_controller` at `/user/hand/left/input/trigger/value`, `/user/hand/left/input/trigger/click` and the corresponding right-hand paths. Axis/click input and both hands merge into one movement request so they do not double speed. Focus or tracking loss requires returning that hand's trigger to neutral before walking resumes. Existing keyboard controls, turning, speed and capsule collision are retained; tested speed remains capped at 360 cm/s.

R07 enables the installed project-local OpenXR plugin and its XRBase dependency, registers the trigger context before XR action creation, and adds a map-only Local tracking-origin helper for the retained elevated camera. Thirty-one software cases passed: 26 raw-key/OpenXR-style EnhancedInput injection cases and five keyboard coexistence cases. Build/cook/stage/archive and a 302-second VR-requested run/window close returned zero, without fatal or material failures. R06 paired traversal reached 14/16 routes before and after with no regression. R07 preserves all 2,232 R06 actors and adds only the origin helper; full R07/headset traversal is untested.

The review computer had no installed SteamVR or selected OpenXR runtime. Its loader could not enumerate runtime extensions and no XR session was created. Software injection and normal-window checks do not establish live SteamVR session creation, actual controller delivery, stereo rendering, camera height, tracking, collision, performance or comfort acceptance. This missing local runtime is a documented testing limit; the user authorized publication of the OpenXR-enabled build. Producer review notes retain the earlier parent-hold wording as historical evidence; this README records the resolved publication decision. R06 local rollback sources/builds and the prior public release remain preserved; no obsolete R06 binary is uploaded here.

Corrected performance disclosure: both R05 and R06 normal runs record six cumulative PSO hitch reports, ending at 300 creation hitches. The earlier R05 phrase-based counter missed these. No frame-rate certification is claimed.

## Reproduction

`scripts` contains the asset cleanup, integration, collision, material repair and review helpers used by the producers. Some scripts retain their original workspace paths and require adapting local input roots. Use exact assets and hashes from the supplied manifests. No tested build was rebuilt or modified during publication; caches, debug symbols and machine-specific logs are omitted from distribution. New raw Epic, MetaHuman and Fab dependency assets are not redistributed.

`CampusCenter_Vive_OpenXR_R07_Source.zip` is the exact frozen 12-file control/configuration delta, SHA-256 `7140087f98be2fcf8cf1daa1b9f8e2fee6b51d62ba06c38973a7d6a28b01666a`; it requires the previously documented baseline and the 39 equipment/trophy/BSOD assets included in the combined source bundle. The R07 map SHA-256 is `ac424605799debdddc8599fdc0741f0cba6d7bafd7fea314d57ead6f4778eac5`. Checksums, runtime file manifests and archive joining instructions accompany the release.
