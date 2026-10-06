# UV02 matched fireplace receiver - compatibility test

[Download receiver/test ZIP](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-p02-p03b3-uv02-receiver-20261006/CampusCenter_P02plusP03B3_UV02_Receiver_Compatibility_Test.zip) (16,219,181 bytes).

Use **only five original P02 1:100 tiles plus the corrected P03 B3 fireplace tile**. The old UV01 receiver remains appropriate for the original P02 prints; this increment does not update the 1:250 sample or other tiles. Overall dimensions remain 657.6 x 512.0602094 x 46.872 mm. Original vertex, face, normal and UV records are byte-identical; 2,756 new fireplace charts use formerly unused atlas space, with an eight-pixel guard around legacy chart rectangles.

Extract all files together. Import `CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj` with the included original-named MTL and `Atlas_Diagnostic.png` alongside it. Preserve model scale, UVs, origin and axes. Apply one complete uncropped 8192-square atlas to every part using unlit/Emission and nearest sampling, without an additional lighting pass. The separately named `Tour_Student_Commons_P02plusP03B3_UV02_Test_Atlas_8192.png` tests fireplace coverage while preserving old chart pixels. Mapped preview images are references, not projection atlases.

**Unchanged old UVs do not mean old media illuminates the new fireplace.** Original textures may leave the appended islands dark. Only this separately named Commons compatibility test is included; full revised tour/animation coverage has not been delivered. Unfinished Ripple/Pac-Man revisions are not part of this release.

This receiver deliberately retains concealed floor/contact faces underneath or behind the appended fireplace to preserve legacy records. It is a projection overlay, **not printable manifold replacement geometry**; print the P03 B3 3MF instead. Fresh Blender import and mapped previews passed, including the fireplace close-up. Actual MadMapper playback, hidden-surface coverage and physical projector calibration remain untested; calibrate and verify visibility on the actual model.

SHA-256: `b5c41c1e0dc8cc48457ab666694137bd42c2c2fb61ad8adc5a236359b36760b2`. Public repack removes one private provenance path from the compatibility manifest and adds publication documentation; geometry, MTL and all image bytes are unchanged. UV01, P02, P03 B3 and prior media/history are preserved. No model/media rebuild or print-package rewrite occurred.
