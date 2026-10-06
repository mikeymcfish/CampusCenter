# Tron T01 UV02 wall-top atlas test

- [Actual8192 UV atlas MOV, qtrle RGB24,10s24fps WALL TOPS ONLY](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-tron-wallcaps-t01-atlas-20261006/Tron_WallCaps_UV02_Atlas_8192_10s24_Lossless.mov) (269,899,016 bytes).
- [Receiver copy, raw atlas keyframes/masks, QA, static Blender preview and reproducible scripts](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-tron-wallcaps-t01-atlas-20261006/CampusCenter_Tron_WallCaps_UV02_T01_Public_Test.zip) (12,819,282 bytes).
- [Public asset checksums](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-tron-wallcaps-t01-atlas-20261006/PUBLIC_DOWNLOAD_MANIFEST.json) (558 bytes).


[Small camera viewing preview and diagnostics](https://github.com/mikeymcfish/CampusCenter/releases/tag/campuscenter-tron-wallcaps-t01-viewing-20261006) are separate; camera images are not atlas input.

Extract the public test ZIP. Use its byte-identical UV02 receiver OBJ with MTL and Atlas_Diagnostic.png together, only five original P02 1:100 tiles plus P03 B3. Preserve dimensions657.6x512.0602094x46.872mm, geometry, UVs, origin and axes. Apply the separately downloaded8192-square lossless QuickTime Animation/qtrle RGB24 atlas MOV to all receiver parts, uncropped, nearest sampling, unlit/Emission, no second lighting pass.10s/24fps/240frames, loop. Static atlas keyframes/mask provide an initial compatibility test. Actual qtrle8192 MadMapper playback is untested. No project/cues supplied.

**WALL TOPS ONLY:**1,006 full-height opaque cap triangles at Z46.872mm,48 mesh-boundary outline paths. Cyan heads/blue trails follow physical arclength around architectural corners. +Z floor-normal/-Z projection sees vertical wall faces edge-on; all side faces are intentionally dark. Shorter partitions, uncertain relief, floors, furniture, glazing, hanging accessories and fireplace are excluded. This is not all-wall or hidden-surface coverage. Real tilted-projector incidence/occlusion requires calibration.

Four representative effect frames show zero leakage at544,068 excluded-face samples per frame plus excluded pixel-square union. Producer decoded MOV samples exactly match source RGB; period endpoint10s equals0s, without duplicate frame in the240-frame movie. Fresh native Blender import and static preview reopen QA passed. Publisher verified original hashes/ZIP CRC, actual atlas codec/dimensions/rate/count/duration and full decoding. Physical projection and actual MadMapper playback remain untested.

Public package removes machine logs/private provenance, excludes derived caches, and makes public script runtime paths configurable. Source scripts compile checked but were not rerun to generate media; original geometry, UVs, movie/image/preview-project bytes and all producer files remain unchanged. Run prepare to reconstruct derived caches before qa/encode; these reproducible commands create outputs only in the extracted test folder. Native .blend is a static QA scene, not the animation itself. All P01/UV01 and prior history/assets preserved. No Library retry.
