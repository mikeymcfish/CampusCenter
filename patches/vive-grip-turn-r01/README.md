## Current main supports the integrated patch

The latest normal root launcher applies and retains this patch using a separate verified managed cache. See [consolidated instructions](../../README_CONSOLIDATED_VIVE.md). The manual steps below and warning describe the original R29 downloader; older main commits still restore unpatched caches.

# Optional Vive GripTurn R01 / PublicGuard R02 patch for exact public R28/R29 builds

Left side grip snaps left 30 degrees; right side grip snaps right 30 degrees, once per distinct press. Release before pressing again. Both held together suppress turning. Focus/tracking loss requires neutral release; collision-aware rotation retains the head pivot. Index-trigger forward and keyboard behavior are retained.

## Install and launch safely

Download `CampusCenter_Vive_R28_R29_GripTurnR01_PublicGuardR02_SmallPatch.zip` from this patch release. No full runtime download is needed if the matching original build is already installed. This corrected guard revision supersedes the unpublished R01 installer ZIP.

1. Close all CampusCenter processes. If R29 is not installed, first use main's `Start_CampusCenter_Vive.cmd` to obtain the original R29 build, then close it.
2. Extract the patch ZIP into the installed build's **Windows** folder beside `CampusCenter.exe`, `CampusCenter` and `Engine`. For the automatic downloader this is `.cc/r29/v/w/Windows` inside your checkout, or `.cc/r28/v/w/Windows` for the previously installed R28 build. Extract the contents, not an extra enclosing ZIP folder. Keep about 1 GB free.
3. Run `Install_GripTurn_Patch.cmd`. It verifies the supported native executable, exact required runtime dependencies and delta/overlay hashes; reconstructs the patched binary; and preserves the original in `_GripTurnR01_Rollback`. Unsupported or changed builds are refused without replacement. No administrator, runtime, registry or rendering-setting change is required.
4. Start SteamVR, connect tracked controllers, then run the bundled **`Start_Patched_CampusCenter_Vive.cmd` in this same Windows folder**. It launches the existing root bootstrap directly. Alternatively run this folder's `CampusCenter.exe`, or the matching existing `Start_CampusCenter_Vive_R29_3050_Compatibility.cmd` / R28 variant in this Windows folder. Return application focus and release the controls before testing grips.

**After installing, do not use the repository-root automatic `Start_CampusCenter_Vive.cmd` to launch this patched cache.** That integrity-checking downloader expects the original executable and exact original files. It will reject the patch and extra payload/rollback files, preserve the modified cache as an invalid folder, then prepare an unpatched original runtime. This patch does not weaken or modify that integrity check.

The separate [optional RTX 3050 CMDs](https://github.com/mikeymcfish/CampusCenter/tree/patch/vive-rtx3050-optional-20261004/optional-launchers/rtx3050) launch the nested executable directly without the main downloader's original-byte check, so they can launch the installed grip patch while retaining their existing process-only quality profile. Keep the matching version's CMD in this same Windows folder. These profiles are not a confirmed performance/headset-freeze fix.

Rollback: close CampusCenter, then run `Rollback_GripTurn_Patch.cmd` in this Windows folder. It validates and restores the original executable and removes only this patch's three overlays. It refuses to overwrite a later update. Preserve `_GripTurnR01_Rollback` and any staging folder for recovery. After rollback, launch Windows/CampusCenter.exe or the optional CMD directly; payload/rollback files still make the strict root downloader treat that cache as modified if you choose to use it again.

For command-line installation without the CMD's pause: `InstallGripTurnPatch.exe install "."`; rollback: `InstallGripTurnPatch.exe rollback "."`, from the installed Windows folder.

## Scope and validation

Source contains five project-owned native/C++ changes and the installer source. Restore the appropriately licensed matching R28/R29 source baseline before applying this overlay; the project is not a standalone Unreal dependency redistribution. Runtime changes are only one reconstructed executable and three small overlay containers. Maps, scene assets, default rendering settings, SteamVR/OpenXR selection and saved starting yaw are unchanged.

Producer software checks passed 20 grip, 26 trigger and five keyboard cases, packaged normal exit zero on both supported versions, idempotence, rollback and tamper/unsupported-input refusal. Actual Vive/controller acceptance, starting-facing diagnosis, frame rate and headset freeze remain unverified. No blind yaw flip or hardware-performance fix is claimed. No screenshots, private machine settings, debug logs or private QA reports are published.
