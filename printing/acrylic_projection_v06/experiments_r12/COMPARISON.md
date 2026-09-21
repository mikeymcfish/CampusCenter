# Projection video comparison

Tested locally on 2026-09-19 with the same iLab opening/closing image and seed 42621. Low-resolution trials were 512 x 512, about 4.4 seconds, 24 fps. This is a small practical comparison, not a model benchmark.

| Method | Observed global drift in sampled frames | Activity | Decision |
|---|---:|---|---|
| LTX-2.3 distilled, identical endpoints | 25.46 px translation, 7.04% scale change | Camera zoom dominates | Reject for projection |
| LTX + static Blender depth, Union Control 0.7 | 0.04 px, 0.006% scale change | Almost frozen people | Reject for walking requirement |
| LTX + animated Blender depth, Union Control 0.7 | 0.05 px, 0.017% scale change | One person gestures/moves, most frozen | Less useful than H3 |
| H3 pruned FL2VA in isolated ComfyUI, identical endpoints | 0.15 px, 0.040% scale change | Clear walking and small gestures | Selected for longer room trials |

Figures come from RANSAC feature fits and are approximate; moving people and repeated furniture can affect them. Contact sheets were also inspected. They do not prove exact pixel registration or guarantee longer clips will behave identically. Long clips must be reviewed separately.

Depth maps were actually rendered in Blender 5.0 from an isolated copy of Source_Studio.blend, using each room's exact original overhead camera coordinates and orthographic scale. Camera Data View Z Depth was saved as raw float EXR and metre-valued NumPy arrays. Technical guides use a fixed 0-4.5 m range with near white, far black, and the original room mask. Both locker rooms (121, 122), commons (102), iLab (108) and gym were rendered. A separate 105-frame Blender sequence included eight proxy people, two following closed paths. Depth was not estimated from color images.

WanGP required mmgp 3.8.0 while the installed environment has 3.7.14. A project-local dependency overlay was used without replacing the installed package. The full H3 WanGP model ran out of GPU memory, then a lower-memory retry caused severe system paging and was stopped. The smaller installed H3 model completed in about 91 seconds through an isolated ComfyUI server on localhost:8191. No unrelated process was stopped.

ImageGen opening frames improve appearance and supply existing people to animate, but are not pixel-exact replicas of the original geometry. Physical projector calibration and full-size alignment remain separate checks. Original models and source image references are preserved.
