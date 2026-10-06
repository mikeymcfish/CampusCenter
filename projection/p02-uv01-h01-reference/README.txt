H01 is a reversible room-to-surface scope/reference supplement to immutable P02 UV01.
It preserves all geometry, vertex positions, UV coordinates, object/material groups,
scale, origin, source files and existing atlas IDs. It is not a MadMapper project,
animation or cue package. No model/UV export is duplicated or replaced here.

The 13 stop identities follow the user list. Entry100 and Reception103 are one
combined stop; Cafe101 and Commons102 are independent. Display Hall106 differs
from Trophy Hall123; ASPIRE112 differs from humanities Collaboration113.
Existing Gym is A101000, retained as the source atlas room code GYM. Trainers129
does not automatically include trainers office127/storage128. Athletics Office
could be124,125,126 or a combination. HS11 stays inactive; its mask is empty,
and three per-room plus all-three candidate masks are provided separately.

Each scale folder has a JSON manifest with exact existing UV01 surface IDs and
numeric room IDs, 13 binary reference receiver masks, a uint8 stop-ID map,
selected/excluded receiver masks, and atlas reference PNG. Black/ID0 means no
reference highlight. The numeric ID map is uint8; binary masks are lossless
1-bit PNGs. At8192 resolution, rows run downward while OBJ v runs upward, exactly
as UV01. Use each scale only with its own existing atlas, not with the other model.
IDs/JSON/CSV list all physical parts; default masks retain the UV01 opaque-only
receiver policy and leave glass, eyelets and undersides unlit. Other geometry
stays in the model. Stop numbers are source-list reference IDs, not cue timing.

Room identities were verified against A101. Surface ownership uses existing UV01
candidate assignments without expanding them. The annotated top map projects
actual unchanged OBJ faces and shows these current candidate assignments; grey
geometry remains. This does NOT newly certify open Cafe/Commons/Gallery/Display
Hall perimeters or shared wall caps. Future final highlights require confirming
those perimeters. No corridor/stair ownership is guessed or extra room added.

The copy folder preserves the exact original14 user-supplied heading/description
pairs separately. The usable13-stop version only combines Entry+Reception,
removes the literal combine instruction, and completes the explicit ASPIRE
placeholder using the official King School heading. All remaining descriptions,
capitalization, punctuation and existing grammar remain verbatim. No editorial
rewrite is applied. Source and precise changes are in Copy_Change_Note.json.
Official ASPIRE source: https://www.kingschoolct.org/academics/advanced-research-program

Publish only this deliverables folder and the H01 package/manifest after validation.
The sole publisher owns GitHub publication. Private helpers, logs, source-plan
crops, baseline file and source models are excluded. H01 can be removed to revert
to unchanged UV01. No original working Blender/Unreal files are changed.
