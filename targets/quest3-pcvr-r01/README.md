# CampusCenter Quest 3 PC-VR R01

Prepared for Windows rendering on Mike's RTX 2080, with Quest 3 connected over USB Link. This is not an Android/standalone headset build. Physical Link, Touch controller and RTX 2080 performance acceptance is pending.

## What is preserved

Uses the verified R29 r02 map and PublicGuardR02 executable, unchanged. Architecture, materials, furniture, artwork, effects, lights, collision geometry, partition states and saved starting yaw remain in the existing containers. Only one mapping-context package is overlaid. All six Vive mappings remain; four Touch analog mappings are added. No MetaXR plugin, app installation, account login, runtime switch, driver update or global renderer/config change is performed.

Installed UE 5.8.2 OpenXRInput already supports `/interaction_profiles/oculus/touch_controller`. Touch keys map to `/user/hand/{left,right}/input/trigger/value` and `.../squeeze/value`. This relies on the runtime accepting the standard Touch profile for Quest 3; actual negotiated profile must be checked on hardware. See [Khronos profiles](https://raw.githubusercontent.com/KhronosGroup/OpenXR-Docs/main/specification/sources/chapters/semantic_paths.adoc).

## Install a separate copy

1. Obtain the existing consolidated main checkout at `31e0e320732852d4b4d7b2fde3b83ea024c12aa5` or its verified successor. Run its normal Vive preparation flow first. The exact R29 grip-enabled runtime resides at `<checkout>\.cc\r29\v\g\Windows`. Close that game before copying. Preserve this source cache.
2. Extract the Quest R01 package into a short path. Verify its supplied ZIP SHA-256. Do not overwrite a previous Quest folder.
3. Run PowerShell from the extracted package:

```powershell
.\QuestPCVR.ps1 -Action Install -SourceWindows 'D:\CampusCenter\.cc\r29\v\g\Windows' -TargetWindows 'D:\CCQuest3R01\Windows'
```

Replace the example source with the actual managed runtime path and choose a new destination on a drive with at least 4 GB free. Installer verifies the exact native executable, bootstrap, 40 published dependencies and all three grip containers before writing; rejects other containers. It copies only the 45 declared runtime files into the new destination, then adds the three Quest overlay files. It does not import Saved settings or mutate the Vive source. An interrupted copy remains preserved; select a fresh destination to retry. No downloads are hidden in the Quest installer.

Scripts use the existing PowerShell policy; they do not bypass or change it. If Windows blocks a downloaded script, stop and review the trusted files/signature/hash with the operator before any file-unblocking or policy decision.

## First USB Link run

Meta software/account/headset setup belongs to the operator and requires separate approval if the assistant is asked to change it. Follow [Meta's current Link setup](https://www.meta.com/help/quest/509273027107091/): use a suitable USB 3 data cable/port, connect the headset, and enter Link. Do not install anything or change the system OpenXR runtime silently. The application uses the currently selected Windows OpenXR runtime. If that is SteamVR, it may run through SteamVR rather than direct Meta Link; direct Meta OpenXR selection is an explicit operator decision. This package does not require SteamVR or force one runtime.

In the Link PC application's device graphics preferences, start at **72 Hz if offered**, with automatic/default render resolution, no supersampling or forced debug-tool encode settings. This is a conservative recommendation, not a measured RTX 2080 result. The launcher does not set headset refresh rate, encode bitrate, codec or USB bandwidth. Record the actual refresh rate and eye-buffer size during hardware acceptance.

From the installed Windows folder run:

```powershell
.\Start_CampusCenter_Quest3_USB_Link.cmd
# Optional edge diagnostics, writing only a task-named log in TEMP:
.\Start_CampusCenter_Quest3_USB_Link.cmd -Diagnostic
# Retained visual settings, without the optional quality profile:
.\Start_CampusCenter_Quest3_USB_Link.cmd -Profile VisualBaseline
```

Default RTX2080 profile requests 3000 MB texture pool with VRAM limit; ray tracing and Lumen hardware-ray-tracing path disabled; 4096 virtual-shadow pages, four rays/four local samples; Lumen gather downsample 16/reflection downsample 2; screen percentage 100 and XR pixel density 0.7; uncapped application FPS. Rendering overrides are command-line Engine ini settings applied before initialization, not saved project edits. They last only for the launched process. They preserve materials and light actors, while reducing rendering accuracy/resolution. Pixel density is a relative request, not a guaranteed absolute eye resolution; verify runtime acceptance in the headset. It represents approximately 49% of the nominal pixel area when the runtime honors it. Monitor window is 1280x720 and is not the headset render resolution. No texture mip cap, blanket object removal or permanent quality reduction is applied. VisualBaseline retains the existing R29 launcher screen percentage 50, with no RTX2080 ini overrides. Both modes retain the baseline-required `-DisablePlugins=MetaHumanCrowdContent` flag; removing it caused an inherited animation assertion in the initial candidate.

At 72 Hz a native full-rate GPU frame budget is about 13.9 ms. Hardware acceptance must distinguish native 72 FPS from runtime reprojection/half-rate operation. If unstable, stop and capture GPU/frame/runtime data before changing resolution or quality further. Do not claim desktop monitor motion proves headset tracking.

## Controls and safe orientation

Either index trigger walks forward at the existing speed; both together do not double movement. Fully releasing both stops trigger walking. Left side grip turns left 30 degrees and right grip turns right 30 degrees, once per squeeze. Touch uses its analog squeeze value, not a nonexistent Vive-style squeeze click. A mapping-local axial dead zone of 0.5 remaps to `[0,1]`; inherited native press/release thresholds correspond to raw squeeze >=0.55 and <=0.525. Release well below half before another turn. The narrow hysteresis and comfortable squeeze strength are software-tested assumptions for later Touch acceptance, not measured ergonomics.

Startup-held controls, simultaneous grips, lost focus and lost tracking require release before rearming. Turning keeps the horizontal head pivot and uses existing swept-body collision checks. Walking while turning follows the new heading. Existing keyboard/mouse behavior remains. There are no Quest-specific controller visuals or redesigned locomotion.

Saved pawn yaw and Local/eye-height tracking origin are retained; there is no automatic 180-degree correction. If orientation is wrong, stop walking, release both grips/triggers, stand safely in place, then use the Quest/Link system's user-controlled Recenter function while facing the intended physical direction. Restore application focus and release controls again before movement. Recenter may change the runtime's reference pose/height; verify view height and body clearance afterward. Its exact Link behavior remains a hardware test. In-app grip turning can adjust the virtual heading without resetting the runtime origin. No app-level reset, forced recenter, boundary change or automatic yaw compensation is added without evidence.

## Verify and roll back

```powershell
.\QuestPCVR.ps1 -Action Verify
# Close the Quest game first, then retire only its overlay:
.\QuestPCVR.ps1 -Action Rollback
```

Rollback moves the three exact Quest files out of Paks into a dated preserved folder and retires the Quest install marker. Native executable, R29/grip containers and all source Vive files remain untouched. The Quest launcher subsequently refuses launch. Use the original consolidated Vive/desktop launchers to return to those versions. Retain the separate Quest copy for investigation; it is never deleted by this script. Unknown asset/hash changes cause refusal rather than replacement. Install again only into a new folder.

## Acceptance still required

Check negotiated Touch profile and four analog actions; left/right snap sign and single-press behavior; release hysteresis, simultaneous suppression, trigger OR behavior; loss/recovery of focus and hand/head tracking; real head pivot/collision; start yaw, user recenter and correct eye height; both partition configurations and accessible routes; material/effect continuity; a sustained Link walkthrough with GPU frame time, VRAM, runtime-reported render size/refresh and normal exit. No physical headset was available during preparation. No GitHub publication is performed by this worker.
