# Longer room results

All selected clips: 768 x 768, 294 frames, 24 fps, 12.25 seconds. H3 pruned FL2VA, 20 Euler/simple steps, identical opening and closing conditioning image. No semantic appearance references.

| Room | Maximum sampled global shift | Maximum sampled scale change | Visual review |
|---|---:|---:|---|
| 108 | 0.167 px | 0.0184% | Accepted after sampled review |
| 102 | 0.037 px | 0.0033% | Accepted after sampled review |
| 121 | 0.131 px | 0.0452% | Accepted after sampled review |
| 122 | 0.248 px | 0.0251% | Accepted after sampled review |
| GYM | 0.091 px | 0.0164% | Accepted after sampled review |

These estimates describe global camera stability, not exact local geometry or flawless human motion. The visual-review record names the inspected artifacts and limitations.

The first commons attempt had one fading student and a student leaving the room boundary. A bounded-motion revision kept everyone inside but briefly duplicated the central walker. The final selected attempt and its exact prompt are included in the room files; rejected attempts remain preserved in the working project.

Projection exports use the original Blender room masks. Every frame of each lossless master was decoded to verify zero RGB outside its mask. A six-frame closing blend returns exactly to its opening encoded frame; raw generated clips retain their original endings.

Actual Blender depth improved LTX camera stability but reduced activity substantially, so H3 matching endpoints was selected. The depth renders and comparison clips are included for further experiments.
