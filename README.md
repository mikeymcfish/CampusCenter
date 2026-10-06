# CampusCenter — current downloads

[Open the current download and source index](PROJECT_DELIVERABLES.md). Older choices are in its history section and the [preserved earlier README](README_HISTORY.md).

## MadMapper: actual projection files

Use the **UV02 receiver with P02 1:100 tiles plus corrected P03 B3**, preserving UVs/origin/axes/scale. This is separate from the optional tracker's 1:250 sample.

- [Download the UV02 receiver ZIP](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-p02-p03b3-uv02-receiver-20261006/CampusCenter_P02plusP03B3_UV02_Receiver_Compatibility_Test.zip); import `CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj`.
- [Ripple R04 actual projection atlas MOV](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-ripple-r04-black-thin-staggered-atlas-20261006/Ripple_R04_Black_Thin_Staggered_Connected_UV02_1_100_4096_Lossless_PNG.mov) — `Ripple_R04_Black_Thin_Staggered_Connected_UV02_1_100_4096_Lossless_PNG.mov`.
- [H04 actual continuous lossless projection atlas MOV](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-h04-atlas-video-r01-lossless-20261006/CampusCenter_UV02_H04_All13_30Pages_300s_ATLAS_8192_Lossless_PNG.mov) — `CampusCenter_UV02_H04_All13_30Pages_300s_ATLAS_8192_Lossless_PNG.mov`, five minutes, 30 static pages held 10 seconds each (0.1 encoded fps). [Original30 source PNG pages](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-h04-all13-30pages-bright-samehue-tour-20261006) remain available.
- [Pac-Man R02 actual atlas movie parts and joiner](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-pacman-r02-uv02-atlas-test-20261006) — join to `PacMan_R02_SingleActor_UV02_1_100_8192_LosslessPNG.mov` before import.
- [Tron T01 actual wall-top atlas MOV](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-tron-wallcaps-t01-atlas-20261006/Tron_WallCaps_UV02_Atlas_8192_10s24_Lossless.mov) — `Tron_WallCaps_UV02_Atlas_8192_10s24_Lossless.mov`.
- [Infinity Rooms R02 actual lossless atlas MOV](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-infinity-rooms-r02-atlas-20261006/Infinity_Rooms_R02_WholeModel_UV02_24s_ATLAS_4096_Lossless_PNG.mov) - `Infinity_Rooms_R02_WholeModel_UV02_24s_ATLAS_4096_Lossless_PNG.mov`, 24seconds at20fps; [fixed-front viewing preview](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-infinity-rooms-r02-viewing-20261006/Infinity_Rooms_R02_WholeModel_UV02_24s_Fixed_Front_Mapped_1024_Viewing.mp4) and [source/QA and optical assumptions](projection/infinity-rooms-r02/README.md).
- [Current B3 fireplace print replacement](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-print-p03-b3-fireplace-20261006/Ground_R29_P03_Tile_B3_1_100_Fireplace.3mf); replace only B3 in the five-other-tile P02 assembly.

**Mapped camera previews are viewing only:** [H04 tour overview](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-h04-all13-30pages-viewing-20261006/Tour_H04_All13_30Pages_Mapped_1024_Overview.mp4) and [R04 mobile preview](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-ripple-r04-mobile-viewing-20261006/Ripple_R04_Black_Thin_Staggered_44s_Mapped_720_Mobile_Viewing_Only.mp4) show the model from a camera; use the actual atlas files above for projection. Mac/browser users can download projection inputs directly; Windows game launchers are a separate target. Actual codec playback/physical calibration in MadMapper remains untested.

## Windows walkthroughs and optional live tracker

Fetch/pull main; keep root launchers with `tools`. Run `Start_CampusCenter_Desktop.cmd`, `Start_CampusCenter_Vive.cmd` or `Start_CampusCenter_Quest3_USB_Link.cmd` for the respective current R29/Quest Windows targets. [Versions and opening instructions](PROJECT_DELIVERABLES.md#current-print-walkthrough-and-optional-tracker). Binary source editing requires `git lfs pull`.

[Optional projector tracker + live R29 sender](targets/projector-tracker-sender-r01/README.md) has its own portable companion/small guarded patch and install/calibration/rollback guide. P02 whole sample **1:250 only**. Existing desktop/Vive/Quest/performance defaults remain unchanged. Actual packaged-game software reception passed; physical HMD/projector/DPI/performance and print-fit acceptance remain untested. Inherited Research doorway/navigation limits remain.

[Verified release sizes/SHA256](FINAL_MEDIA_RELEASE_RECEIPTS.json) · [source/test scope](FINAL_SOURCE_PUBLICATION_NOTES.md) · [older tests and source history](PROJECT_DELIVERABLES.md#history-and-reference-packages).

[Current Ripple R04 / Infinity R02 procedural source and rebuild backup](projection/current-procedural-source-r01/README.md): [sealed source/input ZIP](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-current-procedural-source-r01-20261006/CampusCenter_Ripple_R04_Infinity_R02_Procedural_Source_And_Rebuild_R01.zip), editable generation code, compact geometry, input hashes and reproducible instructions. Seven Ripple and five Infinity keyframes exactly regenerated; full movie rebuilds and clean-machine installation untested. Original trimesh/manifold3d version labels unavailable; fingerprints/exact-array guards supplied.
