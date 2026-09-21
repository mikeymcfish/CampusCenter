Revision 12: tested matching first and last frames.
Open with H3 Studio > Project > Open. Use the FL2VA diffusion model:
minimax_h3_fl2va_pruned_int8_convrot.safetensors.
768 x 768, 294 frames, 24 fps, 20 Euler/simple steps, seed 42621.
Both FIRST and LAST contain the same image. Semantic reference slots are empty.
Do not enable Carry/Chain. Model loader and sampler settings are external to
the project and must be selected in the ComfyUI workflow.
ImageGen images provide appearance and existing people, but are approximate
interpretations of the Blender layout. Inspect generated results before use.
Apply the included original room mask after generation. Masking cannot fix
camera drift or altered interior geometry. Original source models unchanged.
