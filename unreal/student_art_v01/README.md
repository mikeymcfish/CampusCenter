# Student art decals — PC update

Four Imagegen adaptations of flat student work, each with the student's name on a white label:

- Marilyn Sommerville — *The Heart of a Hero*
- Nina Griffith — *Waiting in the Shade*
- Gates Seidelmann — *Plein Air in Chalk Pastel*
- Sophie O’Connor — acrylic graphic composition from her summer-program portfolio

[Open the texture preview](preview.html). The preview applies the same rectangular opacity masks used by the Unreal materials. These are reference-derived AI adaptations, not pixel-exact scans. Reference photographs are retained in `references/`.

## Apply on the Windows PC

1. Close any open CampusCenter Unreal editor session.
2. Extract `Student_Art_Update_v01.zip` **into the existing cloned CampusCenter repository folder**. The archive contains an `unreal` folder that merges with the existing one. It includes the actual textures; it is an update package, not a replacement for the cloned project.
3. Double-click `unreal\Apply_Student_Art.cmd`. This requires the working Unreal Engine 5.8.2 installation. Let texture import and shader compilation finish.
4. Check `unreal\student_art_v01\apply_report.json`. Success is `saved_pending_visual_review`; `failed` includes the error. The updater saves `/Game/Campus/Maps/CampusCenter_StudentArt_v01`.
5. Inspect the saved map in the editor, then use `unreal\Walk_Student_Art.cmd` to explore it. Check artwork orientation, clear labels, and that all four images sit on the intended hallway wall. The original `Launch_Unreal.cmd` still opens the original architect-finish map.

For a nonstandard engine location, set `UNREAL_EDITOR` to the full path of `UnrealEditor.exe` before running the launcher.

## Placement and implementation

The assumed target is the **ground-floor hallway wall alongside the gym, just off the main commons**, not the two small art boards inside the commons. Four canvas centers are at Unreal X = -600, -750, -900, -1050 cm, Z = 175 cm. Each texture canvas is 110 cm tall including the caption. This is presentation sizing, not a claim about original artwork dimensions.

The location is based on the repository's existing Blender hallway-gallery placement at Y = 16.045 m, converted to Unreal's inverted Y. The updater traces the actual wall at five points per artwork and refuses to save when the expected flat wall is not found. If the intended wall differs, update the placement before applying.

Only four `DecalActor` objects are added. Each uses a Deferred Decal material with Base Color, Opacity and matte Roughness; there is no normal/displacement effect. No new static mesh, frame, backing board or collision geometry is created. A 6 cm deep projection volume limits spill through the wall. The updater checks that the static-mesh actor count stays unchanged. Existing architecture, furnishing and other displays remain in the copied scene.

Generated PNG backgrounds are not uniformly usable alpha. The material's two precise rectangular masks isolate the artwork and white name label, removing all surrounding background and ragged edges. **Use the supplied material importer, not the PNG's alpha alone.** The preview shows the effective result.

Re-running the updater on its own target map replaces only its tagged decal actors. It refuses to overwrite an unrelated map at the target path. The original architect-finish map is not saved by this script. No source map or binary Unreal asset has been modified on the Mac.

## Validation status

Checked locally: Python syntax, texture hashes and dimensions, mask bounds/gaps, and visual review of all four masked artworks and labels. Unreal is not installed on this machine, so engine execution, material compilation, collision traces, map saving and in-engine visual review remain **unverified until run on the PC**. Do not interpret the local validation report as a successful Unreal run.

## Sources

Student-to-artwork attributions and reference photos came from the [user-supplied reference archive](https://king-student-art-references.king-school-3694.chatgpt.site/).

- Marilyn: [King School — The Heart of a Hero](https://www.kingschoolct.org/community/news/post/~board/all-school-news/post/the-heart-of-a-hero-earns-marilyn-sommerville-27-international-recognition)
- Nina and Gates: [King School artists receive national recognition](https://patch.com/connecticut/stamford/king-school-artists-receive-national-recognition-nodx)
- Sophie: [Student portfolio](https://www.sophies.studio/sophies-highschool-artworks)

Implementation references: [Epic — Decal materials](https://dev.epicgames.com/documentation/en-us/unreal-engine/decal-materials-in-unreal-engine), [DecalActor](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/DecalActor), [Custom material expressions](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/MaterialExpressionCustom), [map saving API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorLoadingAndSavingUtils).
