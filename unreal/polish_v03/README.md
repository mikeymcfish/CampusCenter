# Campus Center — material and cinematic polish V03

This pass updates the existing Unreal scene without adding props or changing the building layout. The original Blender master is unchanged (SHA-256 `df9a8c1c453a1e4b2885c9e017a2bee4bbd4b811b1078172fa146e161ec09308`).

## Visual changes

- Native Unreal oak materials with CC0 ambientCG Wood049 2K color, normal and roughness maps. Wood, masonry and paving use physical world-space texture scale to correct inconsistent imported UV channels.
- Native masonry, paving, aluminum, stainless steel and dark-metal shaders. Removed the mottled imported normal-map response visible on the fireplace pier and wood panels.
- Corrected woven fabric and painted plaster texture connections. Preserved the reference palette and existing furniture/mannequin geometry.
- Warmer 4200 K interior lights with reduced overlap, controlled exposure adaptation and highlight/shadow local exposure. Subtle bloom and vignette; no motion blur, chromatic aberration or film grain during exploration.
- Lumen GI/reflection quality 1.5, TSR, 16x anisotropy, a 6 GB texture streaming pool, and expanded virtual-shadow budgets. Full-detail ray-tracing fallback meshes preserve the source silhouettes.
- Nine 1920×1080 editor screenshots, with 64 settling frames for high-resolution capture. `../unreal_project/ReviewV03/Cinematic_Review.jpg` is the overview. The commons screenshot camera is offset slightly to avoid a mannequin immediately in front of the lens; the walking route is unchanged.

## Measured performance

RTX 4090, packaged Development build, DX12 and Lumen hardware ray tracing, 1920×1080 at 100% render scale. Offscreen real-time rendering, VSync and frame cap disabled for measurement. Each result uses 1,500 frames after discarding 300 startup frames. Runtime screenshot dimensions and console settings verify the resolution.

| View | Average FPS | 1% low FPS | 95th-percentile frame time |
|---|---:|---:|---:|
| Commons | 116.2 | 85.6 | 9.73 ms |
| Innovation Lab | 104.7 | 73.6 | 10.96 ms |
| Upper commons | 114.7 | 87.8 | 9.89 ms |

Normal exploration is capped at 60 fps. These are stationary-view benchmarks, not a minimum-frame-rate guarantee for the entire route. Other GPU workloads and higher resolutions will change performance. See `performance.json` and `performance_evidence` for measurements.

## Scope and remaining limits

The model retains simplified props and blank static mannequins. Exterior scenery is still sparse, and bright glazing/shadow edges retain some temporal noise. No new people, props, fire or landscaping were added in this material-only pass. Current screenshots are direct Unreal captures, not AI-enhanced images.

Source license and hashes are in `assets/SOURCES.json`. The editable project and rebuilt Windows application are in the adjacent handoff folders. The original migration `Review` and V02 previews are historical, not current screenshots.
