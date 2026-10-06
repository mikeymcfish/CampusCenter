CampusCenter UV02 Infinity Rooms R02 test

First open Infinity_Rooms_R02_WholeModel_UV02_24s_Fixed_Front_Mapped_1024_Viewing.mp4 to review the effect. It is a compact fixed-camera viewing reference.

For projection, use Infinity_Rooms_R02_WholeModel_UV02_24s_ATLAS_4096_Lossless_PNG.mov as the existing UV02 model's texture. It is the complete 4096 x 4096 UV atlas, 20 fps and 24 seconds. Its 480 original PNG packets are copied exactly. Keep the full square canvas and original UV02 receiver; use the existing calibration. The file does not create or modify any MadMapper project, cue or loop setting.

The model has 37 geometry-constrained visual apertures, including non-tour rooms. Cool light contours reveal virtual recessed sidewalls and independently phased descending/returning floors. Complete furniture, tabletop, bench, wall and corrected fireplace footprints stay on stationary protected supports. Their physical mesh and atlas pixels stay fixed. The depth is a colour illusion; the print remains unchanged.

The assumed viewer is at model XYZ (348.25,-600,850) mm, looking toward (348.25,252.875,12) mm, on the south/negative-Y front side. The perspective camera is fixed with 42-degree horizontal field of view. The actual projector pose was not supplied or calibrated. Real walls and fixtures retain their occlusions; one projector cannot be assumed to reach hidden surfaces. Evaluate the depth from this front-side assumption on the real setup.

Black is the chosen background for this test, following the accepted Ripple presentation. Each region completes a smooth 24-second descend/return with a deterministic phase offset. The virtual terminal frame equals frame0 exactly. The last encoded frame is one normal time step before the first. There is no flash, random flicker, noise, bloom or global grid pattern.

Reference_Receiver includes the unchanged four-part UV02 OBJ and MTL. Its SHA-256 is b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba. Model millimetres at1:100, shared world origin, +Z up and +Y north remain unchanged. The actual assembled dimensions are657.6 x512.0602094 x46.872mm. No sample1:250 compatibility is claimed.

QA verifies all480 frames decode, every atlas packet equals its source, exact timestamps, all37 aperture constraints, static fixture pixels, original native vertices/UVs/identity transforms, and all5 actual decoded/native keyframes. The review sheet columns are source mapped, decoded MP4, and fresh Blender; rows are0,6,12,18 and23.95seconds. The floor-aperture plan shows animated areas and protected furniture/supports. Existing open-area divisions are documented visual boundaries inherited from A101/H02/H03/H04; no fresh R29 semantic perimeter audit is claimed.

Physical projection, MadMapper runtime, projector calibration and transparent-window optical behaviour remain untested. The MP4 is lossy; the lossless atlas retains exact source pixels and black background. Original Blender, Unreal, print and MadMapper projects, the prior P01 floor test, accepted Ripple media and tour media remain unchanged.

Producer_Scripts records this authoring pipeline. Its Dependency_And_Input_Record.json identifies the existing producer-workspace inputs. The keyframe/receiver QA kit is not advertised as a standalone rebuild environment; the separate procedural source-backup work remains a later priority. The compact frozen aperture/depth input is included for audit and later reproduction. No full frame/state cache is included in this kit.
