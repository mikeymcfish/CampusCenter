# CampusCenter R27 R13 software-validated review builds

Desktop and OpenXR-enabled Vive review builds include all 66 championship banners, the gym updates, white concentric HVAC diffusers, cleared grass and eight stray step/nosing props hidden with collision disabled. The D-wall platform/bay interpretation remains deferred. Existing release branches, commits and downloadable versions are preserved.

## Download and launch

For a GitHub Desktop checkout, switch to `main`, Fetch origin and Pull origin, then run the root `Start_CampusCenter_Vive.cmd` or `Start_CampusCenter_Desktop.cmd`. These setup launchers automatically download the corresponding pinned release parts, verify checksums, extract the complete build and launch it. GitHub Desktop itself downloads editable source, not the packaged executable. Setup uses a local gitignored `.campuscenter-runtime` folder and needs no token or Unreal editor. The manual release-download method below remains available.

Download all numbered parts for the desired Windows build, plus `ARCHIVE_MANIFEST.json` and `Reassemble-Downloads.ps1`, into one folder. Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\Reassemble-Downloads.ps1`. The helper checks the part count, total size and SHA-256. Extract the resulting ZIP completely before launching; keep the Engine and CampusCenter folders together.

- Desktop: run `Windows/CampusCenter.exe`. Its tested default bootstrap selects `/Game/Campus/Maps/CampusCenter_FA26_Desktop_R27_Enhancements_R13_StrayPropClearance`.
- Vive: run `Windows/Launch_CampusCenter_Vive_R27_R13.cmd`. This portable publication wrapper selects `/Game/Campus/Maps/CampusCenter_Vive_R27_R13_Private_Review` with the exact map, plugin and VR flags used by the producer's absolute-path launcher. The tested executable and game containers are unchanged. The word `Private` remains in the original map name to preserve its identity; the release is public.

On the intended Vive computer, SteamVR must be installed and selected as the active OpenXR runtime, with headset/controllers connected. No installation, global runtime selection or security change was performed here. Hold either trigger to walk forward in the camera/headset's horizontal facing direction; release to stop trigger-only walking. Both hands and trigger axis/click input merge without doubling speed. Focus or tracking loss requires returning the trigger to neutral before resuming. Existing keyboard controls, turning, movement speed and collision are retained.

## What was checked

Desktop R13 cook, normal default launch and normal close passed with exit zero. Visual QA corrections passed: white concentric HVAC diffusers, cleared grass, eight hidden/noncolliding stray props and three clear capsule lanes. The Desktop final map has 2,915 actors.

Vive R13 has 2,917 frozen actors, 369 pinned new assets and 12 unchanged protected control files. Cook/stage and a 302.9-second normal launch/close passed with exit zero and no matched material/shader/fatal errors. R11 passed 26 injected trigger/OpenXR-style cases and five keyboard coexistence cases; final R13 control hashes remain unchanged. The separate scripted CSV capture returned 777003 and is not the successful normal-launch result. No physical Vive/SteamVR session, controller, stereo, camera-height, comfort or headset-performance acceptance was performed.

Two inherited diagnostic failures remain: the offset Research113 doorway probe and the Fitness rack-front aisle probe; alternate probes pass. These are not a certification of all routes or architectural clearances. D-wall platform/bay photo interpretation and measured fidelity remain deferred. Private gym photos informed interpretation but are not redistributed. Physical slicing/print fit remains untested.

## Authentic poster provenance and rights

The six already integrated graphic-only authentic event images are retained in twelve placements at the user's explicit request after disclosure that redistribution rights are unverified. **That approval is not evidence of licensing or rightsholder permission.** Copyright remains with the respective school, artists and partners; public availability is not an open redistribution license. Embedded artist credits, dates and source graphics are preserved. `AUTHENTIC_POSTER_PROVENANCE.json` and `POSTER_ATTRIBUTION_DETAILS.json` identify each graphic and its source.

Additional photo-poster candidates, private original gym photographs, the original mixed poster ZIP, private photo-comparison reports, Library identities and unrelated files are excluded. The old private-only publication gate is superseded only for the explicitly approved six graphics and these integrated versions; it does not establish rights or expand the scope to other images.

## Editable sources and baseline

`CampusCenter_R27_R13_Scoped_Sources.zip` contains project-owned desktop/Vive overlays, public review summaries, provenance and manifests. Restore the appropriately licensed baseline using the [previous R25/R07 release](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-r25-trigger-forward-20261001) and its earlier v26 source instructions; overlay `desktop/project` or `vive/project` into the corresponding Unreal project root. Use the documented UE 5.8 toolchain, compile the included CampusCrowdFix source when needed, and open the exact R13 map listed above. These overlays are not standalone replacements for unredistributed licensed dependencies. No new raw Epic/MetaHuman/Fab/manufacturer assets or model weights are included; necessary tested cooked runtime assets remain intact.

The combined source branch starts at the already public banner-source commit `8edc3fb258f9e454f6e04e7b7f69c93a72f5fb92`, preserving all 66 original source textures and that branch's history. The Vive source branch preserves the previously published `codex/vr` ancestry. Fetch Git LFS when using the source branches. Exact original text bytes are preserved in the scoped source ZIP; Git may normalize line endings. `SOURCE_MANIFEST.json`, runtime file manifests, `ARCHIVE_MANIFEST.json` and `SHA256SUMS.txt` record file mapping, sizes and checksums.

Packaging here creates downloadable archives only. No modeling, game rebuild, recook or alteration of tested executable/container bytes was performed. Debug symbols, temporary caches and machine-specific packaging/debug logs are omitted.
