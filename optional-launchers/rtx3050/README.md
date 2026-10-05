# Optional RTX 3050 Vive launchers (R28 / R29)

This small, optional patch uses the already installed packaged build. It does not download assets, recook, change source/saved settings, install a runtime, edit the registry, replace standard launchers or redesign input. Default main quality remains unchanged.

## Run R28 now

Download `Start_CampusCenter_Vive_R28_3050_Compatibility.cmd` from this folder and copy it into the installed build's **Windows** folder beside `CampusCenter.exe`, the `CampusCenter` folder and the `Engine` folder. For the main auto-downloader's R28 install, that folder is `.cc/r28/v/w/Windows` inside your checkout. Close the currently running game, then run this matching CMD. Use the R29 CMD only with the R29 build; its auto-download install is `.cc/r29/v/w/Windows`.

Rollback: close the game and use the unchanged normal launcher. Keep the optional launcher separate. No manual asset replacement or fresh game download is required for the installed R28 build.

## Changes and limits

The process-only profile requests a 2000 MB texture pool with VRAM limiting, hardware ray tracing off, reduced Lumen/reflection/shadow sampling and resolution, 0.65 XR pixel density and no application FPS cap. Existing 50% screen percentage and monitor size remain. Reduced texture sharpness, eye resolution, shadows, reflections and indirect lighting are expected; objects, native material/light/effect assets and controls remain intact. `patch-settings.json` records exact values.

Both unchanged supplied CMD launchers passed approximately 45-second software launch/normal-close smoke tests with exit zero and no matched material/shader/memory/fatal errors. **Actual RTX 3050 and Vive/HMD acceptance, frame rate and eye-buffer scaling are unverified. This is not a confirmed fix for headset freezing, SteamVR Home overlays, controller failure or intermittent memory errors.** Pixel-density registration was deferred on the test machine without an active XR runtime. The reported ~4 FPS and headset/controller symptoms still require diagnosis on that computer.

After returning application focus, release both triggers before retrying. Tracking/focus safety is retained. Coordinate changes on the Vive computer with the separate SSH owner; these launchers do not change OS/runtime settings.
