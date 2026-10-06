CampusCenter P02 UV01 - approved 13-stop masks and copy - H02

H02 applies the approved scope answer "1. Yes, 2. Stay within": the single
Athletics Office stop includes rooms 124, 125 and 126. Display Hall 106 and
Trophy Hall 123 remain within their numbered areas. Adjoining corridors 110
and 130 remain excluded.

Use this supplement with the existing P02 UV01 model of the same physical
scale. It contains texture masks and reference files. It does not replace
the OBJ, MTL, Blender source, UV atlas, printable geometry or original copy.

Approved stops
01 Entry + Reception: 100 and 103
02 Cafe: 101
03 Student Commons: 102
04 Admissions Office: 104
05 CRI Gallery: 105
06 Corridor / Display Hall: 106
07 Innovation Lab: 108
08 ASPIRE Seminar Room: 112
09 Collaboration Room (humanities research): 113
10 Trophy Hall / Corridor: 123
11 Athletics Office: 124, 125 and 126
12 Athletics Trainers' Room: 129
13 existing Gym: drawn A101 room 000, retained UV01 alias GYM

All 13 stops have nonempty masks at both scales. H02 changes only HS06,
HS10 and HS11 selections. The other 10 selections exactly match H01.

Files and use
assembly_1_100/ and sample_1_250/ each contain the 13 binary receiver masks
in stop_masks/HSnn_Receiver_Mask.png. White is selected; black is excluded.
Each mask is 8192 x 8192 and uses its corresponding model's original UV01
atlas coordinates. Use nearest-neighbour sampling at native resolution.
Do not use the 2048 atlas reference image as a production mask.

Highlight_Stop_IDs_uint8.png stores integer stop indices 1 through 13;
zero means excluded. This is an ID image, not a colour image. Stop_Atlas_
Reference.png is a labelled overview. Selected_Receiver_Mask.png is the
union of all stops. Excluded_From_Highlights_Opaque_Receiver_Mask.png is
the remainder of the unchanged default Opaque receiver. Glazing, hanging
loops and undersides remain excluded. All unselected geometry stays present.

Stop_Selection_Manifest.json and Stop_Surface_Pixel_Coverage.csv list the
active original surface IDs and their pixel coverage. Masks are authoritative:
some original faces/charts cross a hall ownership division. A whole surface
ID on/off switch would reintroduce spill. H02 selects partial texels inside
those charts without changing any original face, vertex or UV coordinate.

Original coarse atlas candidates labelled 110/130 can contain geometry that
physically lies inside 106/123. H02 recovers only the permitted hall portion
by mapping texels through the original triangles into model XY. Their old
numeric room labels do not imply that adjoining physical corridors are lit.

Boundary rules and precision
Boundary_Ownership_Contract.json records exact shared-origin millimetre
bounds, architectural/native wall anchors and source hashes. At open room
junctions the ownership planes extend verified wall alignments. Shared wall
caps divide conservatively at the documented centreline. These are explicit
texture ownership rules; no physical partition or new wall is added.

At crossing triangles, a texel is retained only if all four pixel-square
corners mapped through the original UV triangle lie inside the hall bounds.
Physical triangle/pixel intersection is checked; forbidden shared-edge
coverage vetoes selection. The binary boundary leaves a conservative strip
up to a texel footprint. Linear filtering or downsampling can blur ownership.

The actual 1:250 sample is a separate print adaptation with its own atlas.
Only the ownership planes use the 100/N coordinate conversion. Never obtain
the sample by uniformly shrinking the 1:100 model. Model origin, axes,
transform and geometry remain unchanged. Registration uses the existing P02
coordinate and assembly references; this supplement adds no calibration.

Evidence
Boundary_and_Office_Selection_QA.json independently checks both scales:
all three office receivers form the exact original 124/125/126 union; hall
selected geometry outside the documented bounds is zero; physical adjoining
corridor 110/130 coverage is zero; unsupported selected texels and stop-mask
overlaps are zero; the default Opaque receiver partition is complete.
Hall_Face_Clipping_Register.csv records source-face boundary relationships.
Source_Preservation_Hashes.json and Final_Package_QA.json verify all 261
source and H01 baseline files remain unchanged.

Annotated_H02_13_Stop_Room_Map.png is a static reference sampled from the
unchanged actual primary model and its original UVs. The before/after UV
chart comparison and model difference diagnostic show removed spill,
recovered hall coverage and the combined office selection. The top reference
shows visible upper surfaces; production masks also cover eligible wall faces.

Copy
The four copy files are byte-identical to H01. Original wording is retained,
including capitalization, punctuation and grammar. H01's only authorized
copy changes remain the combined Entry + Reception stop and the full ASPIRE
program name. No further copy edits were made in H02.

Publishing and limits
Hand this additive supplement to the sole publisher. Parent-reported current
main: 4d4f2938294ce3c1f10e84abae3add280da12f81. There is no GitHub push here.
No animation, cue, MadMapper project or physical projector calibration is
included. Original Unreal/Blender work and earlier print packages are intact.
No installation, print job or unrelated filesystem cleanup was performed.
