# CampusCenter P02 player projection companion R01

Windows x64 WinForms app. Sharp white dot on ground floor; a soft Gaussian dot upstairs at the same fixed XY. Invalid/lost tracking, 500 ms stale telemetry and positions outside the exact P02 foundation footprint hide the marker. This uses an ordinary projector, no laser and no extra Unreal scene render.

## Run the portable build

Extract `CampusCenterTracker_R01_Portable_Windows_x64.zip` into a writable folder. Double-click **Start_Tracker.cmd**. Everything needed is inside, including a private copy of the installed .NET 9.0.4 Windows runtime. No install/admin rights/network download is needed. Keep `app`, `runtime` and both CMD files together. `Start_Tracker_Simulator.cmd` starts a clearly labeled synthetic OSC stream; stop it before using the real sender. Close the control window to stop its simulator, receiver and projector output.

The app starts in **Preview / calibration**, with output closed. The display dropdown deliberately starts unselected. Select the actual secondary projector display and click **Open selected projector**. The primary/game display is refused. If only one display exists, use the control preview; no display configuration is changed. Output closes if the selected display disappears, becomes primary, or its resolution changes; it never moves to a fallback monitor. Refresh displays and recalibrate after a display change. Saved profiles do not auto-open output.

## Align to the physical sample

Use the unchanged **Ground_R29_P02_Sample_1_250** whole print, approximately 263.36 × 196.8 mm. The larger 1:100 / UV02 assembly is not supported by this profile. The shown outline comes from the sample's actual z=0 foundation boundary, including its three small cutouts; it is not an atlas or a rectangular coverage approximation.

1. With the real projector aimed at the model, choose **Preview / calibration**. Align the outline, grid and L01–L10 reference crosses to the sample. The grid is spaced at 20 model mm. The L markers are inherited architectural reference points converted from 1:100 by 0.4, independently checked against world coordinates; verify their actual physical counterparts, especially wall-edge points.
2. Adjust **Translate X/Y %**, **Scale** and **Rotation degrees**. Translation is in the fixed model-bound plane: +X right/east and +screen Y down/south before rotation. These controls do not change telemetry registration.
3. Adjust **Point 1 TL, 2 TR, 3 BR, 4 BL** output X/Y percentages to correct the floor-plane perspective. These four controls map the model bounding-plane corners to projector pixel fractions via a homography. The bounds corners may lie outside the irregular physical foundation; use the visible foundation outline and known landmarks to match/extrapolate them. Convex, uncrossed points are required; invalid edits are refused. Keep the projector/print fixed after calibration.
4. Use test X/Y mm, yaw and Ground/Upstairs/Invalid to inspect mapping without game telemetry. Test-pose controls are available only in preview. A canvas click sets an approximate unwarped test XY; numeric XY is authoritative after warping.
5. Set a visible **Sharp radius px** and **Upstairs blur sigma px**. Dot size can be larger than scale. The optional heading arrow defaults off; upstairs uses a faint arrow if enabled. At yaw 0 it points +world X, at +90 it points +world Y (south in this model frame). Changes to heading, dot size or blur do not move XY.
6. **Save profile** persists to portable `app/data/calibration.json`. **Load saved** restores values and selected device without opening output. **Reset calibration** closes output and resets all calibration values in memory; Save to persist reset. Close/relaunch loads only saved values. `--profile "path.json"` supports an explicit alternate profile file. Copy this file to preserve calibration.
7. Choose **LIVE telemetry** after alignment. The projector shows black with only the tracked dot/optional arrow. The control window retains source, floor, age, coordinates and accepted/rejected counts.

Four-point correction is for the floor plane. Raised walls, furniture, glazing and translucent parts can create parallax/reflections; alignment and visibility on a real printed sample must be tested physically. No MadMapper project or model changes are supplied.

## Use live Unreal coordinates

Start the companion before the sender/game. Receiver binds **127.0.0.1:9001 only**; a second receiver causes a clear bind failure. The sender is a separately owned, opt-in Unreal integration; see [TELEMETRY_CONTRACT.md](TELEMETRY_CONTRACT.md). Stop the built-in simulator first. The source indicator says **SIMULATOR** for `sim-` sessions and **UNREAL telemetry** for `ue-` sessions. A `ue-` label alone is not proof of packaged-game validation.

Sender must report camera/HMD world XY including room-scale movement, heading, classified floor, tracking validity and teleport/recenter flag at about 20 Hz. Ground/upstairs classification belongs to sender and must use reliable floor/body references, with hysteresis; tall gym ground-floor voids must remain ground. Missing pose, lost tracking or unknown floor must send validity 0. Same XY upstairs on the ground sample is intentional. Fixed registration is:

```
model X mm = (UE world X cm + 4700) / 25
model Y mm = (-UE world Y cm + 230) / 25
```

No smoothing: the marker takes every accepted position directly, including teleports. Duplicate/out-of-order/malformed/wrong-profile/nonfinite/retired-session packets do not refresh tracking. Shared-PC UTC timestamps additionally reject queued old packets. Receive staleness uses a monotonic clock, so clock changes do not extend visibility. A receiver restart clears session history; a sender restart uses a fresh UUID.

Open/calibrate the control UI before VR play, then return focus to the game. The borderless secondary output is shown without activation and ignores mouse activation/input, has no taskbar entry and never requests focus. The ordinary control window can take focus when the operator clicks it. Do not calibrate while walking in VR. This companion makes no input, performance-profile, launcher, OpenXR, OS monitor or firewall changes.

## Simulator and evidence

Simulator uses the exact OSC codec over UDP loopback into the production receiver. Each 20-second cycle shows ground (0–5 s), upstairs (5–10), invalid (10–12), silence/stale (12–14), teleported ground (14–17), outside sample (17–20), then repeats. Simulator positions are synthetic. Stop/start creates a new session. If a live sender competes, stop the simulator and restart the receiver/sender deliberately.

`qa/Companion_UI_simulator.png` is an actual WinForms DrawToBitmap capture during received simulator telemetry. `qa/evidence/*` uses the production renderer with labeled synthetic poses. Ground_sharp and Upstairs_blurred use the same [140,125] mm XY for direct comparison. `_output.png` files show exact black-only output appearance. These are software screenshots, not a photo of projection. `--evidence "folder"` regenerates them. `--smoke "folder"` runs a 6.1-second simulator/UI check, records local runtime path and upstairs screenshot, then closes without opening a projector.

## Build and QA

Installed SDK 9.0.203, WindowsDesktop 9.0.4 reference packs. No NuGet packages; NuGet.Config clears remote sources. Run `./build.ps1 -Test`. Builds/tests write only under this folder. UI tests need a Windows interactive desktop; the restricted execution shell's window drawing can fail. The desktop-capable test path is required. Profile generator `tools/derive_p02_profile.py` reads the original sample OBJ and registration read-only; its default source path is Tank-specific. Runtime profiles are already supplied, so no original OBJ/Python is needed to run.

QA covers independent OSC fixture, known coordinates/heading, exact footprint cutouts, sharp/blurred marker, invalid/stalehide, teleport, session restart/reconnect, malformed/truncated messages, out-of-order/timestamp guards, shared clock jumps, loopback socket exclusivity, display refusal, normalized DPI mapping, profile save/load, and UI launch/close/relaunch. See [QA.md](QA.md) and `qa/QA_RESULTS.json` for measured scope.

The portable runtime is copied from Tank's installed .NET 9.0.4, with LICENSE and ThirdPartyNotices included. No software was installed or updated. The companion can be reviewed/published independently; only the designated publisher should push to GitHub. Unreal sender owner must supply its own source/build/integration QA. Existing R29, Vive grip/trigger, Quest Touch, desktop and performance settings are untouched by this companion.

References: [OSC 1.0 wire format](https://opensoundcontrol.stanford.edu/spec-1_0.html), [WinForms ShowWithoutActivation](https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.form.showwithoutactivation?view=windowsdesktop-9.0).
