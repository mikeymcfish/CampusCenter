# CampusCenter projector sender R01

This optional patch connects the R29 Vive / Quest PC VR game to the P02 projector companion on the same Windows PC. It sends the existing player camera's world position over loopback. The companion displays a sharp ground-floor dot and a blurred upstairs dot at the same XY. Lost tracking, unsupported floor or loss of game focus hides the dot.

The patch preserves R29 geometry, materials, lights, effects, Vive grip / trigger controls, Quest Touch mappings and existing rendering profiles. It creates no additional rendered camera. Original game folders remain available for rollback. No runtime, monitor, firewall, security or installation settings are changed.

## Install into a new copy

You need the existing **grip-enabled R29 Vive runtime**, or the existing **Quest PC VR R01 runtime** if you want to retain Quest Touch support. This patch requires native SHA256 `20adab2cd975e19d325adbe607b907cfffa2bd3e775b01c51a68f695bfdf915a` and verifies its runtime dependencies. It refuses older or unknown builds and unrecognized containers.

1. Prepare the current Vive download with `Start_CampusCenter_Vive.cmd -PrepareOnly` in the existing GitHub checkout. Its managed grip-enabled source is normally `.cc\r29\v\g\Windows`. For Quest, use the already installed Quest R01 Windows folder instead.
2. Extract `CampusCenter_ProjectorSender_R01_Optional_Patch.zip` into a separate folder.
3. Run this command, replacing both paths. The destination must not already exist:

```powershell
powershell.exe -NoProfile -File .\ProjectorSender.ps1 -Action Install -SourceWindows "<chosen Windows folder>" -TargetWindows "<chosen Windows folder>"
```

The installer copies the verified game into the new folder, reconstructs the new native executable, adds the small OSC metadata overlay, and checks every hash. It retains the optional Quest overlay only when it is already present and verified. It preserves the original source. If a preflight check fails, correct the identified source or choose a new destination; preserve incomplete output for review.

## Run

Open the companion first, select and calibrate the actual secondary projector, and select its live-player mode. Stop its simulator before starting the game. The companion opens no projector automatically and refuses the primary game display.

In the new installed game folder, run **Start_Vive_Projector.cmd** or **Start_Quest_Projector.cmd**. These explicitly opt into the sender. Vive retains the inherited R29 fullscreen 1920 x 1080 / 50 percent screen-percentage startup arguments and FPS display. Quest retains the existing Quest R01 RTX2080 profile; `-QuestProfile VisualBaseline` selects its existing alternative. This patch makes no runtime selection or device installation. Use the already configured SteamVR / PC VR environment.

Return focus to the game after operating the companion controls. On desktop software review, click the game viewport before walking. The marker hides while the game lacks focus. A real headset remains required to accept room-scale HMD tracking and VR controls. Quest standalone Android deployment is not part of this Windows patch.

The underlying script defaults to verification. A launch without `-EnableSender` runs the preserved game without telemetry. Explicit launch example:

```powershell
.\ProjectorSender.ps1 -Action Launch -Mode Vive -EnableSender
```

To verify the installed copy, run `ProjectorSender.ps1 -Action Verify`. To roll it back, close that game and run `ProjectorSender.ps1 -Action Rollback`. Rollback verifies the baseline native backup, retires the sender native and metadata files into a timestamped folder, and checks the original game and retained Quest overlay. Use the original launcher afterward; preserve the retired folder.

## Verified scope

- Exact OSC v1 schema, UDP 127.0.0.1:9001, actual UTC decimal milliseconds, fresh session / sequence / teleport behavior, fixed P02 registration, camera offsets and nominal 20 Hz: 291 actual native sender packets, measured 19.83 Hz.
- Development packaged R29 to the sealed production companion: 779 accepted real snapshots, zero rejects, visible marker, stale hide after the game stopped, normal window close / exit 0. No simulator or fake focus was used in this packaged acceptance.
- Native sender to the same production companion in a transient PIE support fixture: 283 accepted snapshots, zero rejects, visible ground and upstairs at matching XY, invalid hidden and stale hide. This fixture explicitly simulates focus and supplies test support platforms; it is not a physical headset or upstairs-route acceptance.
- Input regressions with the sender enabled: 20 Vive grip, 26 trigger, 5 keyboard and 29 Quest Touch cases pass. Hardware tracking / focus is explicitly simulated in these software input suites.
- Editor, Development and final Shipping source builds pass. Shipping packaged runtime to the production receiver: 777 accepted real snapshots, zero rejects, visible tracking, stale hide and normal exit 0. Shipping logging remains disabled as inherited; material / shader log checks come from the Development run.
- Consumer installer, existing-destination refusal, unknown-container refusal, exact native reconstruction and rollback pass. All 48 original Vive / Quest source files remain unchanged. The metadata overlay preserves all 233 original plugin entries and adds OSC only; its empty IoStore companion contains no asset packages.

R29's inherited collision and navigation limits remain. Floor detection uses the character's walkable support, with hysteresis between ground and upper level; it does not infer upstairs from HMD eye height. Unsupported or flying positions are invalid. A tall ground-floor gym does not become upstairs when the camera rises. No scene collision repair, renderer reduction, extra art or furniture is included.

Actual headset tracking, SteamVR / Quest operation, physical projector alignment, secondary-display / DPI transitions and hardware frame performance remain unverified. The P02 whole sample's actual footprint and cutouts remain the companion's coverage authority. Its 1:250 world registration is `Xmm=(Xcm+4700)/25`, `Ymm=(-Ycm+230)/25`.

## Publisher / source integration

Only the designated publisher should push or publish. The source-and-QA archive supplies the new native sender files, additive OSC dependency changes, generated game target source, build / packet / receiver / input / rollback evidence and exact file hashes. Apply only the listed source changes to the corresponding R29 source. Preserve target-specific maps, startup configuration, controls and performance settings; do not replace a desktop map with the Vive map or overwrite unrelated project changes.

The review patch targets the exact R29 Vive / Quest Windows baseline. Desktop keyboard behavior is validated in that runtime; this does not certify migration into a separate desktop map / native build with a different dependency closure. Other baselines require their own guards and acceptance.

No push, public release, Blender export, print change or art / furniture migration was performed by this task.
