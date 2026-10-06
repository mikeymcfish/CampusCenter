CampusCenter Tron wall test T01 — UV02 — 6 October 2026

PLAY / TEST
Watch deliverables/Tron_WallCaps_UV02_FrontNormal_Mapped_1024_10s24.mp4.
This 1024x786 mapped-camera video is for viewing. It is NOT atlas input.

The projection input is deliverables/Tron_WallCaps_UV02_Atlas_8192_10s24_Lossless.mov.
It is one complete 8192x8192 fixed UV02 atlas: 10 seconds, 24 fps, 240 frames,
silent, lossless QuickTime Animation / qtrle RGB24. Apply the same complete,
uncropped atlas to every receiver part using unlit/Emission, nearest sampling,
no additional lighting. Loop playback. Keep black as black. Playback in
MadMapper has not been tested. Four native-resolution PNG atlas samples and
the selection mask are supplied for a static compatibility test first.
No MadMapper project, cues or application installs are included.

RECEIVER / ASSEMBLY
Use the supplied byte-identical receiver_copy OBJ, its original-named MTL and
Atlas_Diagnostic.png together. Existing UV layout, dimensions, placement,
origin and axes are preserved. Numeric units are model millimetres, +Z up.
Physical assembly: five unchanged P02 1:100 tiles plus P03 B3 fireplace only.
Overall dimensions: 657.6 x 512.0602094 x 46.872 mm.
Receiver SHA256: b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba
Reference release:
https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-p02-p03b3-uv02-receiver-20261006
The fireplace geometry is preserved and intentionally stays dark in this wall
test. Do not substitute UV01 or the 1:250 sample.

WHAT IS SELECTED
The first test selects 1,006 upward opaque wall-cap triangles at the shared
architectural cut height Z=46.872 mm, covering 9,565.4978 square millimetres.
It traces 48 closed outlines extracted from their actual mesh boundary edges.
Moving cyan heads and blue trails use physical path arclength, so they turn
architectural corners independently of atlas islands. Occasional gold pulses
are restrained. All effect frames are free of text and room numbers.
This conservative first test omits shorter partitions and uncertain relief.
Glass, furniture, floors, underside/contact surfaces, hanging accessories and
the appended fireplace are excluded. Tiny isolated full-height structural
caps can appear as small pulses; no connecting light is invented across gaps.

SINGLE-PROJECTOR LIMIT
The model is NOT physically calibrated. The front-normal assumption used here
is an orthographic projector along -Z, normal to the model floor XY, with +Y
at the top of the preview. This matches the published mapped-view convention.
The visible effect is on upward wall TOP CAPS. Vertical wall faces are edge-on
in this assumption and cannot receive a useful full-face image. Slightly
sloped faces may have grazing incidence; this test conservatively leaves all
wall-side faces dark. The wall-top trace is intentional. No hidden surfaces
or complete vertical-wall coverage are claimed. A physical tilt could change
incidence and occlusion and needs its own calibration and visibility test.

QA / DIAGNOSTICS
WallCaps_Static_FrontNormal_Mapped_1024.png: static selection in the actual
front camera mapping, with model occlusion from the verified UV02 cache.
Tron_QA_FrontNormal_Mapped_00..03_1024.png: times 0, 2.5, 5, 7.5 seconds.
Tron_QA_NativeBlender_FrontNormal_1024.png: fresh native OBJ import / real UVs.
Tron_QA_NativeBlender_Oblique_1024.png: same cap-only effect from an oblique
camera; diagnostic viewing direction, not a second projector or visibility claim.
WallSelection_Oblique_DIAGNOSTIC_1024.png: cyan caps, violet adjoining wall-side
faces, grey excluded geometry. These colours identify classes; this is NOT
projection media. UV02_WallSides_DIAGNOSTIC_8192.png is likewise diagnostic only.
UV02_WallCaps_Selection_8192.png includes 4x4 triangle-edge antialiasing and
four-pixel copied-colour gutters restricted to empty atlas space. Every atlas
pixel square intersecting an excluded triangle vetoes selection. There is no
rectangle fill and no triangle-border animation.
qa/Representative_Frame_QA.json samples seven barycentric points on EVERY
excluded face: 544,068 points per frame, all zero RGB, plus the full excluded
triangle pixel-square union. qa/Final_Media_QA.json tests actual decoded MOV
pixels, dimensions, frame count, periodicity, motion and source hashes.
Mathematical time 10 equals time 0 exactly. The 240-frame sequence omits a
duplicate endpoint so the last-to-first step continues the motion naturally.
No physical projection or MadMapper playback verification has been performed.

SOURCE / REPRODUCE WITH INSTALLED SOFTWARE
Source code is in source/. The .blend preview project packs the time-0 atlas
and preserves all imported receiver geometry and UVs. It is a STATIC QA scene;
build_test.py generates the actual animation from physical outline arclength.
camera_mapping.npz contains the read-only UV02 published front-view UV lookup.
Runtime requirements: Python with NumPy/Pillow/SciPy, Blender5.0, FFmpeg/ffprobe. Public scripts use the bundled receiver copy, current Python interpreter and FFmpeg on PATH (or CC_FFMPEG). No packages were installed by publication. Set CC_FFMPEG if your installed FFmpeg is not on PATH. Run from this folder:
  python source/build_test.py prepare
  python source/build_test.py qa
Inspect the masks and QA frames before the following long step:
  python source/build_test.py encode
  blender --background --python source/render_diagnostics.py
  python source/verify_media.py
Derived caches are excluded from the public package; run prepare before qa/encode.
Each command writes only to this isolated test folder. Receiver files and
another producer's source/output folders are never overwritten.
SHA256SUMS.txt and SHA256.json identify deliverables. No GitHub push was made.
