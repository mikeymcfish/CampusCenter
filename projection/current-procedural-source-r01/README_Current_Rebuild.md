# Current CampusCenter procedural source and rebuild bundle

This backup contains the actual generation code and compact inputs for the current **Ripple R04** and **Infinity Rooms R02 test**. Infinity R02 is awaiting user visual review; this backup makes no animation revision. Historical Ripple R03 generation is also retained. There are no movies, animation frame sequences, stored height states, original project files, or third-party executable runtimes in the ZIP.

`Production_Script_Provenance.json` links the bundled production scripts to their original SHA-256 hashes and records portability changes. `Bundle_File_SHA256.json` lists every included file. `R04_Rebuild_Config.json` records all77 source events and solver/transfer parameters. `Infinity_R02_Rebuild_Config.json` records all37 regions, fixed camera, phases, depth and colour equations, and pixel hashes for five current keyframes. These configuration files are records of the constants in the preserved generation code, rather than parameter-override interfaces.

## Inputs and environment

The bundle includes1,284 exact frozen native actor NPZ geometry files, all56 locked physical domains, complete operational native ownership/obstacle data, the full projected furniture obstacle grid, accepted world-boundary polygons, source masks/patches, and the compact Infinity aperture/depth input. All are identified by relative path and SHA-256 in the input registries and full file manifest. The native actor vertices are centimetres with Y already reflected; extraction applies `(vertices+[4700,230,0])*0.1` and adds4.2mm to Z. Re-extraction from the original Unreal project is outside this backup; the exact extracted geometry actually consumed by the accepted pipeline is supplied.

The two receiver meshes are already published. `resolve_public_inputs.py` resolves their exact bytes from a frozen repository checkout/receiver ZIP or downloads them from the explicit immutable identifiers in `External_Receiver_Input_Manifest.json`:

- UV01: repository commit `74081e3fb86e879085c371853f66fc34f70053a6`, SHA-256 `5fb3d64faebe846255f84b4e4f2be832070fec649ea99a1005d69f0c802db45f`.
- UV02: the published R04 receiver kit, archive SHA-256 `a44a71da3c9d080978d7404b0141aea6e8679e04a09f072458cacf6d0accd97d`, receiver SHA-256 `b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba`.
- Shared MTL: SHA-256 `8f71eea8b37df7d0705cdfa9f69afde3d0fbde5cd8e524e04ae4b4f88de3c715`.

Use64-bit Python3.12.14, NumPy2.3.5 and Pillow12.3.0. The exact production environment and FFmpeg build/hash are in `Environment_Requirements.json`; requirements files list the Python packages. FFmpeg needs PNG and libx264 for the current movies. Historical R03 additionally uses HAP/Snappy and Windows Segoe UI. Supply FFmpeg and ffprobe on PATH, or provide both explicit paths. The runner does not install packages or software.

Blender5.0.0 is optional for native keyframe reapplication; its factory Cycles seed is0 and animated seed isFalse, with4samples and the documented camera/colour management. The numerical generators use no PRNG: their seed is `null`; source order, events and region phase offsets are explicit.

Default generation uses the included verified domains/apertures, requiring only NumPy/Pillow plus FFmpeg for encoding. Optional native physical-domain re-extraction also needs trimesh and manifold3d. Their original distribution version labels were not retained; exact source/module fingerprints and a successful fresh native extraction comparison are provided. Regenerated arrays must equal the locked references before rendering. No release versions are guessed.

Allow approximately16GB RAM and20GB free scratch space for both full stages. R04 height states alone occupy11,309,315,668bytes. Infinity needs roughly1GB scratch for its480 paired frames and movies. These large generated outputs are excluded from the backup.

## Prepare and verify

Extract the source ZIP, then validate it:

```powershell
python verify_source_bundle.py
python run_rebuild.py --workdir 'D:\Scratch\CurrentSourceCheck' --download --prepare-only
```

Preparation copies hash-verified sources/compact inputs into a **new or empty** workspace and resolves the exact receiver meshes. It runs no full simulation or movie encode. For offline preparation, replace `--download` with `--repo 'D:\FrozenCampusCenterCheckout' --receiver-zip 'D:\Downloads\CampusCenter_UV02_Ripple_R04_Keyframes_Receiver_and_QA.zip'`.

From that prepared workspace:

```powershell
python verify_rebuild.py --build-caches
python verify_infinity_rebuild.py
```

The Ripple check re-executes all77 accepted events, tests reflection/isolation, performs a3-second real Gym solve and rebuilds the world/UV caches. Its recorded state hash identifies the accepted frame60. `--production-root` optionally reads the original stored fields to compare seven exact Ripple transfer keyframes. It never writes to the original workspace. The Infinity check executes the actual current generator using the compact geometry inputs and fresh UV02 front visibility; it must match all five recorded atlas/mapped RGB pixel hashes and the exact terminal loop state.

## Full current generation

Run from the extracted source bundle and choose a different fresh workspace:

```powershell
python run_rebuild.py --workdir 'D:\Scratch\CurrentFullRebuild' --download --revision all --ffmpeg 'D:\Tools\ffmpeg.exe' --ffprobe 'D:\Tools\ffprobe.exe'
```

Use `--revision r04` or `--revision infinity` to build one current effect. Add `--blender 'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe'` for native keyframe renders. Without Blender, the Infinity media QA explicitly records the native comparison as not run; paired-source decode checks still run.

Add `--regenerate-native-domains` to derive physical domains from the included actor meshes. Add `--regenerate-infinity-apertures` to rerasterize full print-mesh obstacles and recompute all first-exit rays from the room boundaries. The runner checks every regenerated array against the locked references before proceeding.

Ripple R04 stage order:

1. Optional native extraction: `ripple_r02_domains.py --whole-model`, then `ripple_whole_fixture_volume_audit.py --connected`.
2. `ripple_r04_staggered_solver.py`:56 physically connected domains,77 fixed source locations, deterministic staggered times,64seconds/1281 stored states.
3. `ripple_r04_parallel_preview.py`: accepted44seconds,880frames,20fps,4096-square atlas PNGs and paired1024x786 viewing media.
4. Compact decode QA, lossless atlas MOV, lossless mapped reference MOV and crest-width QA scripts.
5. Optional `hybrid_media_native_preview.py` with exact-black world.

`ripple_r04_thin_ridge_transfer.py` supplies the preserved generation functions. Its historical standalone main branch attempts64-second media and contains early descriptive strings. Use the runner/parallel-preview entrypoint for current44-second R04. The ridge half-width is0.85mm and the quiet threshold0.00007mm, as recorded in the configuration.

Infinity Rooms R02 stage order:

1. Optional `production_navigation.py` and `infinity_rooms_preflight.py`: actual full overhang/obstacle raster, inherited room polygons intersected with physical domains, protected supports, and exact cell-by-cell first-exit depth rays.
2. `infinity_rooms_preview.py`: actual37-region shader generation,480 paired frames,24seconds/20fps, fixed front camera, compact mapped MP4.
3. Optional `infinity_rooms_native_preview.py`: all four unchanged UV02 parts in a fresh Blender scene.
4. `infinity_rooms_media_qa.py`: paired-source decode/motion checks and actual4096-square PNG-in-MOV atlas, with every PNG packet checked against its source. `--skip-native` records omitted optional native comparison.

The original `infinity_rooms_finalize.py` is retained delivery-packaging provenance. It depends on the original workspace preservation baseline and existing accepted media; the portable runner does not call it. It is not needed to regenerate either current movie. Historical R03 can be requested with `--revision r03`; its original40-second solver/transfer remains available. The mobile R04 transcoder is historical and checks the exact original mapped master hash.

## Verification scope and limits

The supplied QA documents exact fresh native physical-domain extraction, exact current source schedule, the bit-identical short Gym state, exact rebuilt world/UV caches, seven Ripple transfer keyframes, and five Infinity atlas/mapped keyframes. The isolated rebuild check also recomputes current navigation/aperture data from the public receiver and verifies all compact geometry arrays.

This backup verification does not rerun the entire64-second solve or re-encode the complete880/480-frame movies. Their original full production decode/packet QA is supplied as evidence. Exact MOV/MP4/PNG **file** hashes can differ with FFmpeg, x264, zlib/Pillow builds; compare decoded pixels and recorded numeric/input hashes. Fresh package installation and a complete clean-machine movie rebuild are untested. Native library release metadata is incomplete, with fingerprints and exact-array guards supplied. Renderer/encoder output across different platforms is not promised byte-identical.

Infinity R02 retains the assumed south/front viewer, existing open-area texture boundaries and real mesh occlusion; it awaits user review. Existing native warnings, tiny unexcited physical pockets, inherited boundary limits, projector calibration, transparent-window optics and physical MadMapper/projection testing remain unchanged. No original geometry, UVs, project, accepted movie or published history is modified by preparation or verification.
