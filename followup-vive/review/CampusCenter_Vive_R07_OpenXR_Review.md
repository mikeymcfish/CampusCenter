# CampusCenter Vive R07 OpenXR activation review

## Software result

R07 enables the installed UE 5.8.2 OpenXR project plugin, packages its loader and requests VR through the review launcher. Build/cook/stage/archive exit 0. A 302-second VR-requested launch and normal window-close exit 0. This is an XR-configured software build; no real XR session was created on this machine.

## Required project changes

OpenXR activation brings its installed XRBase dependency. The existing trigger mapping context is registered before XR action creation, without automatic activation in unrelated maps. A new R07-only non-colliding helper requests application Local tracking origin for the already elevated, HMD-locked first-person camera. No floor-height guess, recenter or world-scale change. The review launcher adds -vr and selects R07; original default map is retained.

## Controller and movement checks

Vive profile /interaction_profiles/htc/vive_controller binds either hand trigger value/click to per-hand highest-absolute-value Axis1D actions. One horizontal camera-yaw forward request per frame; release stops trigger-only motion. Focus/tracking loss requires release before resuming. All 26 input cases passed: 13 raw-key cases and 13 EnhancedInput action-injection cases matching the installed OpenXR input route. Five keyboard coexistence cases also pass. Existing speed, collision and turning retained; tested speed stays capped at 360 cm/s.

## Preservation

All 2,232 R06 actors and existing dependencies match; R07 has 2,233 actors, adding only the origin helper. Nine original protected files remain unchanged; exactly two configuration exceptions are OpenXR activation and trigger-context registration. Rendering, materials, lights/effects, input assets and original maps remain. R06 source and review archive are frozen rollback authorities.

## Exact runtime blocker

SteamVR was not found in any of the four registered Steam libraries. Standard HKLM and HKCU OpenXR ActiveRuntime values are absent, and XR_RUNTIME_JSON is unset. The packaged OpenXR loader reports extension enumeration failure and no active tracking provider. It cannot establish SteamVR operation without runtime setup. No installation, OS active-runtime selection or security/permission change was performed.

## Remaining acceptance

The parent must resolve authorization for SteamVR installation/runtime selection on the intended hardware, then test actual Vive session creation, tracking, trigger press/release, reconnect/focus, camera height, collision, frame rate and comfort. These diagnostic cases simulate head yaw, tracking and focus; they do not prove hardware bindings or stereo rendering. R06 reached 14/16 route probes with two inherited obstructions; full R07/headset traversal is not certified. Cold-start PSO hitches remain disclosed; settings preserved.

## Review and publication

C:\Users\mikef\Documents\Codex\2026-09-30\task-3\CampusCenter-vive\review_build_vive_openxr_r07_r01\Windows\Review_CampusCenter_Vive_R07_OpenXR.cmd
Use this launcher to select R07 and request VR. Raw executable retains the original default map. Use frozen R06 archive/launcher for rollback. Parent owns publication and its readiness hold; no independent push.

## Authority and evidence

Installed OpenXR.uplugin and OpenXRInput.cpp define plugin dependencies, Vive profile handling and default mapping-context consumption. Epic SteamVR guidance: https://dev.epicgames.com/documentation/unreal-engine/developing-for-steamvr-in-unreal-engine?lang=en-US . final-control-handoff.json pins source/archive/evidence hashes; control-source-manifest.json includes the 12-file source ZIP, binding paths and official references. runtime-validation.json includes actual plugin/loader/registration/failure log evidence.
