# Tour static test textures — Production P01

Four actual **8192×8192 UV atlases** per scale: Student Commons, Innovation Lab, ASPIRE Seminar Room and Cafe. All official title/body copy is inside the gym, without room-number labels; furniture uses contrasting surfaces and baked contact shading.

- [Physical1:100 ZIP](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-tour-statics-p01-20261006/CampusCenter_P02_UV01_P01_Tour_Static_Examples_1_100.zip) — includes exact matching UV01 OBJ, presentation MTL, four atlases, mapped/native-emission previews and QA.
- [Physical1:250 ZIP](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-tour-statics-p01-20261006/CampusCenter_P02_UV01_P01_Tour_Static_Examples_1_250.zip) — includes exact matching UV01 OBJ, presentation MTL, four atlases, mapped/native-emission previews and QA.

Extract the package for your actual printed scale. Import its exact Model OBJ as a 3D surface, preserving UVs/origin/axes. Add a `*_Atlas_8192.png` to the Media Bin and assign the full uncropped image to the complete model. Use native resolution and nearest/point sampling; avoid extra lighting/shadow passes. Switch the four atlas media to test the examples. Mapped previews, normal-view previews and Gym_Caption_Reference images are reference images, not projection textures. Full scale-specific instructions are in LOAD_IN_MADMAPPER.txt.

Source geometry and UVs are unchanged; the copied presentation MTL supplies a convenient initial atlas binding. The1:250 sample has its own atlas and print adaptations; do not uniformly rescale the1:100 mesh. Approved H02 masks constrain the selected room; remaining rooms are black except the gym copy. Assumes a single projector roughly normal to the floor from +Z. Hidden-wall illumination is not claimed.

Fresh Blender import/reapplication and source/texture registration checks passed. **Physical projection and actual MadMapper playback remain untested**; calibrate the projector to the real model. No MadMapper project/cue programming is supplied. Infinite Floor/Ripple Rooms are published incrementally after their separate checks; Pac-Man awaits a final validated handoff. Original packages/history are preserved; public metadata removes private paths.
