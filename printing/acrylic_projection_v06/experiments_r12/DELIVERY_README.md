# Campus Center projection loops — revision 12

This delivery compares four local generation methods and uses the best observed result: H3 FL2VA with the same image assigned to both the first and last frame. Additional appearance-reference slots are empty. The short comparison used the iLab; the selected method was then used for five longer room clips.

## Room outputs

| ID | Room |
|---|---|
| 108 | Innovation Lab |
| 102 | Student Commons |
| 121 | Locker Room 121 |
| 122 | Locker Room 122 |
| GYM | Gym |

Each clip is 768 × 768, 24 fps, and 294 frames (12.25 seconds). The students are already present in the ImageGen opening image. The same image supplies the closing frame. This helps retain the overhead framing and return to the opening arrangement; it does not guarantee perfect human motion or a mathematically seamless loop.

Open `index.html` through the existing local project server to view the clips and comparison. Files under `rooms/` include:

- `<ID>.mp4`: masked H.264 playback preview.
- `<ID>_Projection_Lossless.mkv`: FFV1 master with exactly black RGB outside the original Blender room mask, verified by decoding every frame.
- `<ID>_raw.mp4`: unmasked model output, preserved separately.
- `<ID>_Start.png`: the image used at both endpoints.
- `<ID>_Prompt.txt`: readable prompt with robust ASCII punctuation.
- `<ID>/`: generation workflow and technical measurements.

Use the lossless master where exact black boundaries matter. H.264 compression can introduce slight edge bleed. Import the CGlide project with **H3 Studio > Project > Open**. Its README identifies the external model and sampler settings; project import does not select the ComfyUI model loader for you.

The final six frames of each projection export gently blend back to its first encoded frame. The lossless master's first and last frames are therefore identical. This removes the endpoint image jump; it does not make every generated footstep or turn physically exact. Raw clips retain the model's original ending.

## Blender depth tests

The depth folder contains actual Blender camera-depth renders for all five rooms: float EXR distances in metres, 16-bit normalized depth, and 8-bit control images. Camera position and orthographic scale match the original room render contract. Normalized guides use a fixed 0–4.5 metre range, with near surfaces white and far surfaces black. The original room masks supply the black background.

An additional Blender sequence animates proxy people and provides genuine per-frame depth. Both static and animated depth were tested with LTX Union Control, using the rendered maps directly rather than estimating depth again from a colour image. See `COMPARISON.md` for the observations and method-selection rationale.

## Practical limits

ImageGen starts are visual interpretations of the original room layouts, not exact CAD projections. Reapplying the room outline prevents projection outside that outline, but cannot repair altered interior geometry. Feature-registration measurements estimate global movement and may be influenced by moving people or repeated furniture. Physical projector calibration and alignment to the printed model are still required.

The original Blender scene and prior delivery remain unchanged. Reproduction scripts retain the local project/runtime paths used for this experiment and require those installed models and dependencies.
