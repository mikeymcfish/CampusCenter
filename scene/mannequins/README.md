# Baked student mannequins - revision 16

The current scene contains 112 original, simple, blank mannequin figures: 56 male-proportioned and 56 female-proportioned teen reference bases. These are schematic proportions, not anatomically detailed human models. There are no clothing meshes, facial details or textures.

## Performance and visibility

All 112 figures are in **STUDENTS - toggle entire collection**. Disable that collection to hide them. Each student is one ordinary mesh object. The scene uses 26 shared pose/seat-fit meshes, totaling 59,363 unique vertices. There are zero armatures, pose constraints, student animation tracks or live modifiers. Blender file size grew by approximately 1.6 MB relative to the previous scene.

Thirty-six figures are seated: 15 in the commons, seven in the iLab, eight in upper-level areas and six elsewhere. The remainder use relaxed, weight-shifted, listening, conversational, reading/holding and walking stances. Walking is a static posed stance; it is not an animation. Seating is fitted to chair centers, back orientation and seat height. Legs are adjusted for seat height while soles remain near the floor.

## Reuse and editing

`Mannequin_Pose_Library.blend` contains 13 baked poses for each base. Append a figure from that file, or duplicate an existing student. Use linked duplicates (Alt+D) for the same pose to share mesh data; make the mesh single-user before editing only one copy.

The figures were authored locally for this project. They are not downloaded MakeHuman or Mixamo assets and have no third-party runtime dependency. `source/mannequin_library_v16.py` contains the editable joint positions and body proportions. `source/build_mannequin_library_v16.py` rebuilds the 26 library figures using headless Blender; it writes an `output_v16` directory beside the script. The joint definitions generate and bake the geometry directly, so there are no skeletons to load or delete in the delivered scene. `pose_library.json` records the joint coordinates and geometry counts. The standalone library keeps every pose available, including a standing workbench pose not used in this placement pass.

## Verification

Blender and GLB were reopened, including all 112 students in the GLB. Source geometry and transforms outside the student collection are unchanged. The existing 5,517-frame walking camera is retained. The pose meshes have no non-manifold edges. Source scene, floor-height, placement and texture checks passed; representative commons, lab and classroom images were visually reviewed. Reading/holding poses are blank hand gestures without books or tablets. No new walkthrough video was rendered.
