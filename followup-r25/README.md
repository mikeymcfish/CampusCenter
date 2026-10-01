# CampusCenter R25 follow-up

This follow-up adds fourteen improved equipment assemblies, cleaned silver cup and regional plaque display assets, and a fictional static BSOD on reception TV65. The earlier v26 final release remains available and unchanged. The BSOD is decorative artwork, not an operating system error or slideshow.

## Downloads and desktop launch

Download every numbered `CampusCenter_Desktop_R25_Windows.zip.partNN` file, `ARCHIVE_MANIFEST.json` and `Reassemble-Downloads.ps1` into one folder. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\Reassemble-Downloads.ps1`. Extract the resulting ZIP completely, keeping `CampusCenter` and `Engine` beside `Windows/CampusCenter.exe`. Launch that EXE; its tested bootstrap opens R25 automatically.

The equipment ZIP contains editable Blender geometry, GLB exports, source scripts, dimensions and checks. `SilverCup_Ready.zip` and `RegionalPlaque_Ready.zip` contain editable Blender/FBX/GLB outputs, preview images and provenance. These are manually cleaned Trellis hybrids with blank plates, not authentic award replicas or fabrication unions. Model weights and rejected prototypes are excluded. Ready-package notes describe the asset-preparation stage; final integration and package review records are in `desktop-review`.

`CampusCenter_R25_Combined_Delta_R02.zip` contains 39 new Unreal assets and one new map, `/Game/Campus/Maps/CampusCenter_FA26_Desktop_R25_CombinedReview`. Apply it to the appropriately licensed editable desktop baseline documented in the [v26 final release](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-v26-final-20261001). This delta is not a standalone Unreal project. Do not overwrite previous maps. Third-party raw dependency exclusions and the packaged application's end-user notice remain in effect.

## Validation and limits

Desktop cook, packaging, default-launch smoke and saved native geometry/material checks passed. The two final trophy actors explicitly use NoCollision; original cases retain BlockAll. Sixteen distinct paired walking routes across the R22/R24 and final R25 records show no new regressions. Two inherited failures remain: Research113_25 and Fitness_RackFront_Aisle. Original approved case footprints and seven corrected bench donors are preserved. Scoped visual evidence is included; some fine contacts are dark or occluded.

Cold and warm launch observations include shader/PSO hitches and an audio-buffer underrun. Frame-rate performance is not certified. Equipment mechanics, heights and clearances are inferred, not manufacturer or architect certified. Actual headset/controller testing and physical slicing/print fit remain untested.

## Vive controls and package

Final trigger-forward implementation, exact controller bindings, package version and validation evidence will be recorded here after the final validated Vive handoff. This staging document is not a publication announcement.

## Reproduction

`scripts` contains the asset cleanup, integration, collision, material repair and review helpers used by the producers. Some scripts retain their original workspace paths and require adapting local input roots. Use exact assets and hashes from the supplied manifests. No tested build was rebuilt or modified during publication; caches, debug symbols and machine-specific logs are omitted from distribution. New raw Epic, MetaHuman and Fab dependency assets are not redistributed.
