# R01 software QA and remaining acceptance

`qa/QA_RESULTS.json` records 16 grouped checks on Tank. Code has no external package dependencies. UI testing used the desktop-capable execution path after Windows GDI rejected drawing in the restricted shell; the identified hung test was terminated and the socket released. The final UI test requires actual `sim-` telemetry received over UDP, not only a visible form.

| Area | Software evidence |
|---|---|
| Registration | Independent world formula and inherited landmarks ×0.4 agree; actual sample SHA-256 pinned in P02_REGISTRATION_AUDIT.json |
| Footprint | Four exact z=0 triangle boundary loops; rejects points inside bounding rectangle but outside foundation |
| OSC | Independent 176-byte Python fixture matches; every truncated prefix, unknown tags/address, trailing/bundle data, invalid flags/session and nonfinite/inconsistent XY rejected |
| Tracking | Sharp ground, same-XY blurred upstairs, immediate invalid hide, exactly 500 ms monotonic stalehide, exact teleport snap |
| Ordering/restarts | Duplicates/out-of-order/old timestamp/retired session rejected; new session and stale reconnect recover; competing active sender refused |
| Clock | UTC forward/backward jump recovery with increasing sequences; receiver monotonic timeout unchanged; queued old/future packet rejection |
| Calibration | Four corners match homography; heading axis/sign and rotation checked; malformed/degenerate/crossed/null profiles refused |
| Persistence/DPI | JSON save/load restores display and coordinates; normalized transforms agree at 1280×720 versus 1920×1080; resolution change refuses output |
| Display policy | Empty selection, primary display and changed resolution refused in logic tests; missing selected device never opens output |
| Rendering | Real Gaussian falloff beyond sharp radius; hidden output sampled black; exact production renderer generates evidence |
| Socket/lifecycle | OS listener = 127.0.0.1 only; duplicate port bind refused; invalid packet does not prevent stalehide; dispose/rebind works |
| WinForms | Actual window responds, receives simulator, leaves foreground handle unchanged in quiet mode, captures bitmap and closes/relaunches |

Portable smoke QA additionally runs the final WinExe using bundled private runtime and records the actual runtime path and upstairs received telemetry in `qa/portable/PORTABLE_SMOKE.json`. This is simulation, not a packaged Unreal game test.

Remaining acceptance requires equipment/integration:

- Real secondary projector connection: select identity, open borderless output, verify pixel alignment, no focus/input capture, disconnect/reconnect/move/resolution changes. Tank exposed one 2560×1440 display during software QA. No OS monitor settings changed; no primary-display output opened.
- Real monitor DPI changes at 100/125/150% and saved-profile reload: normalized arithmetic is tested; actual monitor DPI transitions are not.
- P02 print/projector: align landmarks, set visible dot size/blur, check wall parallax and translucent reflections. No physical calibration or optical claim.
- Unreal sender/package: room-scale HMD world XY versus pawnroot; valid tracking/focus loss; floor classification and gym void; heading, stair hysteresis, recenter, teleport, sender restart and shutdown. Sender source/build and package installation are the Unreal owner's responsibility.
- Real Vive grip/trigger, Quest Touch and desktop acceptance, sustained HMD frame time with and without telemetry. Companion does not modify those inputs or settings. No HMD performance claim.

No GitHub push, Unreal asset edits, MadMapper project, laser hardware, software install, LAN listener or firewall rule was made by this companion task.
