# Infinity Rooms R02 actual lossless projection atlas and QA

Actual 4096x4096 PNG-codec UV02 projection atlas MOV, 24 seconds, 20 fps/480 frames. Use the unchanged P02 plus P03 B3 1:100 UV02 receiver (SHA256 b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba), full atlas without cropping/repacking, original registration and calibration. Not the tracker 1:250 sample. Companion MP4 is a mapped camera viewing preview only.

Whole-model eligible floors form 37 geometry-constrained virtual apertures with cool descending contours/planes and smooth staggered return on black. Full furniture footprints are protected and static throughout; physical geometry stays at actual heights. Virtual depth is an optical design, not physical movement or new walls. Assumed single projector and fixed front viewer on south/negative Y looking north (eye348.25,-600,850 mm; target348.25,252.875,12 mm; horizontalFOV42 degrees); actual mesh occlusion retained and hidden-surface illumination not claimed.

Publisher full decoding, size/SHA256, receiver hash and QA archive CRC verified. Producer all480 PNG packets match source, all480 static furniture/support pixels and five decoded/native keyframes reviewed; 317 protected original files unchanged. User review, Mac/MadMapper import/performance, actual projector calibration, front-side apparent depth and transparent-window behavior remain untested. Boundaries inherit A101/H02/H03/H04 references, not a fresh R29 semantic audit.

QA ZIP includes keyframes, unchanged receiver references, geometry/depth arrays, provenance scripts and input hashes. It is not a complete standalone producer environment. Existing media and all deletion candidates are preserved.


## Downloads

- [Infinity_Rooms_R02_WholeModel_UV02_24s_ATLAS_4096_Lossless_PNG.mov](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-infinity-rooms-r02-atlas-20261006/Infinity_Rooms_R02_WholeModel_UV02_24s_ATLAS_4096_Lossless_PNG.mov) (236,646,404 bytes), SHA256 `bb43f36cc6b2a2526ff5eb7bdbf75188da075abe30e57e89b1df2ae03ca11abe`.
- [Infinity_Rooms_R02_WholeModel_UV02_24s_Fixed_Front_Mapped_1024_Viewing.mp4](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-infinity-rooms-r02-viewing-20261006/Infinity_Rooms_R02_WholeModel_UV02_24s_Fixed_Front_Mapped_1024_Viewing.mp4) (686,269 bytes), SHA256 `fed0f3f0ab7aac94d037f835bc5c7cc692c0e6117a092ee19f65446877f04a83`.
- [CampusCenter_UV02_Infinity_Rooms_R02_Keyframes_Receiver_And_QA.zip](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-infinity-rooms-r02-atlas-20261006/CampusCenter_UV02_Infinity_Rooms_R02_Keyframes_Receiver_And_QA.zip) (9,166,671 bytes), SHA256 `ad8637732a7dd82ab786ae7bb4132468e5cf8e11d1a9a0af71bc45ca1c483bc3`.

A separate [current procedural source and rebuild backup](https://github.com/mikeymcfish/CampusCenter/tree/main/projection/current-procedural-source-r01) now supplies actual generation code and compact inputs: [download sealed ZIP](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-current-procedural-source-r01-20261006/CampusCenter_Ripple_R04_Infinity_R02_Procedural_Source_And_Rebuild_R01.zip). Earlier QA archives retain their original limited scope. Seven Ripple and five Infinity keyframes regenerated exactly; full movie rebuilds/clean-machine installation remain untested and two native library release labels are unavailable.
