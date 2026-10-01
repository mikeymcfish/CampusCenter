# CampusCenter final V26 — 1 October 2026

The finalized architectural prototype, artwork integration, furniture update and print deliverables are published here without rebuilding the reviewed models or packaged applications. `main`, `codex/vr` and the working revision retain their history. The `final-v26/` directory identifies the current release; inherited files elsewhere are earlier project history.

[Download the final release](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-v26-final-20261001). Use the named release assets below rather than GitHub's automatically generated source ZIP, which contains Git LFS pointers.

| Deliverable | Final version / location |
|---|---|
| Corrected editable Blender model | `final-v26/blender/Campus_Center_New_Plans_Furniture_v26_b05.blend` |
| Desktop source overlay | `final-v26/unreal/desktop/CampusCenter.uproject`, final map `CampusCenter_FA26_Desktop_R21_Support` |
| Vive source overlay | `final-v26/unreal/vive/CampusCenter.uproject`, final map `CampusCenter_Vive_FA26_R04_Support` |
| Tested desktop Windows application | `CampusCenter_Desktop_R21_Windows.zip.partNN` release downloads; launcher `Windows/Start_Enhanced_CampusCenter.cmd` |
| Tested Vive Windows application | `CampusCenter_Vive_R04_Windows.zip.partNN` release downloads; launcher `Windows/Review_CampusCenter_Vive_FA26_R04.cmd` |
| Print editable scene, STL, 3MF, STEP, previews and manifests | `CampusCenter_Furniture_Print_V26_R02.zip`; editable `CampusCenter_Furniture_Print_Edit_R02.blend` in `final-v26/print` |
| Artwork sources, textures, FBX/GLB, originals and validation | `final-v26/artwork/`, ART26_R01; 11 unique presentations, 12 original photographs |
| Shared accepted furniture/art overlay | `final-v26/shared/shared_furniture_art_v26_r03` |
| Final fitness collision/support patch | `final-v26/shared/fitness_support_v26_r02`; R01 is obsolete |
| Corrected final review and supporting evidence | `final-v26/reviews/` |
| Reproduction scripts and byte manifests | `final-v26/scripts/`, `SOURCE_MANIFEST.json`, release runtime manifests and `SHA256SUMS.txt` |
| Convenient downloadable source set | `CampusCenter_Final_Sources_V26.zip`; project-owned source overlays, not the restricted dependency library |

## Download and run

Download every numbered part of the application you want, plus `Reassemble-Downloads.ps1`, `ARCHIVE_MANIFEST.json` and `SHA256SUMS.txt`, into one folder. Verify checksums with `Get-FileHash -Algorithm SHA256 <filename>`. Run `powershell -ExecutionPolicy Bypass -File .\Reassemble-Downloads.ps1` from that folder to reconstruct the ZIPs, then extract each ZIP completely. Keep the `Windows` directory and its contents together. Read `END_USER_NOTICE.txt` and launch the named command file. Do not run from inside a ZIP. The desktop and Vive packages are separate applications; do not combine their `Windows` folders.

The original final-map launchers and runtime bytes are preserved. The published packages omit debug symbols, machine-generated packaging lists, transient logs/caches, and the optional engine GPU dump inspection tool. None is required by the tested application. No recook, asset stripping from cooked containers, or model rebuild was performed.

For Vive, install the appropriate SteamVR/OpenXR runtime and use the included final review launcher. Hardware headset/controller interaction remains untested; the launcher's review settings are retained exactly as tested. A successful desktop review is not verification of a headset session.

## Open sources

Open the `.blend` files in Blender. Print exports are available directly in the print ZIP; read `ASSEMBLY_AND_LIMITS.txt` and the delivery/changed-piece manifests before slicing.

Unreal project descriptors specify engine **5.8**. Install that engine and the required Epic plugins separately. The published Unreal sources are overlays containing final project-owned maps, furniture/art/support assets, configuration, and the CampusCrowdFix project plugin source. Compile that plugin locally through Unreal before opening; editor-linked plugin binaries are not included. They are **not self-contained editor projects**. Reconstruction steps: (1) restore the preserved desktop baseline commit `bba09634bc610e4b71586523b8d7a7b7f8586ddd` or Vive baseline commit `db5b1cec11adbdf25b2df4e1615d00d5f009fc82` into a separate project, (2) restore missing licensed content and plugins from authorized channels and verify their paths/hashes against `BASELINE_DEPENDENCIES.json`, (3) overlay the matching `final-v26/unreal/<desktop|vive>` folder, (4) compile CampusCrowdFix with Unreal 5.8/MSVC 14.50 and a Windows SDK, and (5) open the named final map. Missing dependency permissions or unavailable exact hashes block a faithful editor reconstruction; the packaged application does not need those raw sources. Keep desktop and Vive editor projects separate. Select the named final map explicitly; the preserved configuration may still reference inherited baseline maps. Check shared patch dependency manifests and source inventories before applying scripts. Scripts retain original project paths and require local path configuration; do not blindly run them on the only copy of a project.

To clone binary source files, install Git LFS, clone the appropriate release branch and run `git lfs pull --include="final-v26/**" --exclude=""`. Verify binary files against `SOURCE_MANIFEST.json`; Git may normalize line endings in text files. Release source ZIPs contain actual source bytes and preserve text bytes, independent of LFS.

## Redistribution constraints

The full local editable Unreal projects include Epic/MetaHuman Crowd source assets and Fab/PN foliage and other downloaded content. `BASELINE_DEPENDENCIES.json` records exact baseline file hashes, engine association, enabled plugin identities, and the MetaHumanCrowdContent descriptor (version 1.0, engine 5.8.0, beta). It also records dependent plugins MetaHumanCharacter, MetaHumanCrowd, DrawDebugLibrary and MovieSceneAnimMixer. Fab vendor listing IDs and package version numbers are not preserved in local metadata; they are explicitly marked unknown instead of guessed. Original component handoff notes may describe local editor binaries; this public overlay includes project plugin source only. Those raw assets and engine code/tools are not newly uploaded in this release. Required licensed baseline content must be acquired through the original authorized channels. See [Epic Content License Agreement, sections 3–4](https://www.unrealengine.com/eula/content), [Unreal Engine license](https://www.unrealengine.com/eula/unreal), and `THIRD_PARTY_SOURCES.md`. Public source sharing is not a grant of third-party redistribution rights. Manufacturer Formlabs CAD and raw reference collections are likewise outside this new source set; a public download is not an unrestricted redistribution license. Existing repository history is preserved.

Print geometry regeneration prerequisites are retained under `final-v26/CampusCenter-print-r25-r01`, at the sibling location expected by the R02 generator. Install its pinned `requirements.txt` into a separate environment. The original R01 comparison script is historical evidence and additionally needs the prior R01 set; it is not needed to regenerate R02 geometry. STEP export additionally requires OCP/OpenCascade. Paths for Blender extraction and Unreal scripts must be configured for the local checkout. These scripts have been published without rerunning the model/build pipeline.

The cooked runtime applications retain necessary licensed content as part of the application. The separate end-user notice disclaims warranties and liabilities for Epic and other licensed content and grants no right to extract and redistribute it. No blanket open-source license is introduced for student artwork, school plans or third-party assets.

## Known limits

Headset/controllers have not been tested. Physical print slicing, tolerances, assembly and fit have not been tested. The inherited Research doorway obstruction and navigation limits remain. Artwork includes photo-based presentations of sculptures and garments, not complete volumetric replicas. This prototype does not establish construction, accessibility or life-safety compliance.

Verified final Vive map SHA-256: `66bb8a995287aec326302d992b8dada72202477584ac96a7a68f35aa874c037c`.

Verified final fitness R02 `manifest.json` SHA-256: `27f4cfb83f647a28ea322aaa26ecac1a0ea5c7327a0c36af095798af722c3678`. Consult per-file manifests for the entire patch.
