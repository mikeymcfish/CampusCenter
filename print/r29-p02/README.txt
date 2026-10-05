CampusCenter R29 PRINT REVISION P02 - ground-floor open-roof display
Matte white PLA / transparent PLA; two 0.4 mm nozzles

P02 CHANGES
P01 incorrectly excluded ground-intersecting architecture with Upper in its
actor name. P02 restores all seven gym perimeter segments in the sample and
tiles, retaining three doorway openings. The four confirmed CF27 UpperCurve
seat/base pieces are ground Commons furniture and are included at native
positions. Ground portions of affected stair rails are restored; roof and
actual upper-floor layout remain outside the ground-display scope. Native
R29 meshes/world bounds and A101 gym footprint/openings were checked.

PRINT FILES AND MATERIALS
Ground_R29_P02_Sample_1_250.3mf is the hook-free whole-layout sample.
Ground_R29_P02_Tile_A1 through B3_1_100.3mf are six separate print plates.
A1-A3 are the south row; B1-B3 the north row, viewed with NORTH up.
Tiles are rotated 90 degrees on their print plates; use manifest transforms
to assemble. Both complete eyelets and their roots belong to B2 only.

There are exactly TWO filament materials and THREE named geometry regions:
Opaque -> extruder 1, matte white PLA.
Glazing -> extruder 2, transparent PLA.
HangingLoops -> extruder 2, the SAME transparent PLA as Glazing.
B2 has Opaque and HangingLoops, with no architectural Glazing. Sample and
other tiles have Opaque/Glazing. 3MF standard base materials and part/extruder
metadata are included. Confirm these assignments in your slicer. This is
geometry 3MF, with no G-code or complete machine/process preset.
For STL alternatives import each tile's material files as parts of ONE object
and retain their shared coordinates. Do not arrange materials independently.

SIZE AND STATIC FIT
Sample 1:250: 263.36 x 196.8 x 19.0688 mm.
Six-tile assembly 1:100 including eyelets: 657.6 x 512.06021 x 46.872 mm.
Architecture/foundation footprint remains 657.6 x 492 mm. Shared origin,
scale, internal seams, native transforms and UV canvas are unchanged.
The full 1:100 REFERENCE.3mf and Combined_REFERENCE.stl are assembly
references, too large for one H2D plate. Print the six tile plates instead.

All seven print plates pass static H2D shared dual-nozzle bounds:
X=25..325 mm, Y=0..320 mm, conservative Z=320 mm, 5 mm model brims.
A 60 x 60 mm purge tower body plus provisional 5 mm brim is reserved at
X=65..135, Y=242..312 mm. Rear wrapping detection exclusion is retained
at X=145..256, Y=310..320 mm. Tightest reserved model-to-tower gap: 4.992 mm.
B2 including eyelets occupies 265.98521 x 216.70833 x 46.872 mm on its plate.
Check actual tower dimensions, brims, travel, supports and assignments in
your slicer; a larger generated tower needs new clearance checking. Keep
wrapping detection enabled. No slicer software was installed or run here.
Official source profiles used for the static bounds:
https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/machine/Bambu%20Lab%20H2D%200.4%20nozzle.json
https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/process/0.20mm%20Standard%20@BBL%20H2D.json

EYELETS AND GLUED ASSEMBLY
H01/H02 sit outside the NORTH gym edge near its west/east ends, flat on the
print bed. Nominal clear holes 8 mm; outside ring diameter 20 mm; minimum
radial ring section 6 mm; outboard ring/stem thickness 6 mm. Print tolerances
may change hole clearance. Ring/stem transition has broad flat gussets.
Each 36 x 24 mm flared tail has a 26 mm exit neck and is buried 2.8 mm deep
under the existing white 4.2 mm foundation, leaving at least 1.4 mm white
capture skin. The dovetail-like root and skin restrain sliding and lifting;
this does not depend solely on adhesion between PLA colours. White top
projection-floor height is preserved. Use solid/dense eyelet and capture-root
zones in slicing; hollow sparse roots are not the intended implementation.
Native architecture is unchanged by these user-authorized print accessories.

Superglue the six tiles on a flat backing/alignment surface using the common
bottoms and straight seams. Prepare and fully cure joints according to the
adhesive maker. The eyelets, PLA creep and six glued tile joints have NO
certified load rating or physical strength verification. Before hanging,
perform a supported load test of the fully cured assembly and use a safety
line. Do not hang over people. Transparent PLA strength and optical clarity
have not been physically tested.

GLAZING AND PRINT ADAPTATIONS
All 54 ground-scope native architectural glazing components are covered:
26 door lights and 28 other components, merging into 47 connected volumes.
Newly restored sources add no ground glazing. Mirrors, screens, display-case
glass and water are separately classified and are not architectural glazing.
Glazing is closed volume, thin principal axes expanded symmetrically to at
least 1.2 mm before ground clipping. Opaque thin principal axes are 0.8 mm;
structural sampling 0.4 mm tiles / 0.16 mm sample; heights quantized 0.2 mm;
opaque simplification 0.01 mm. Furniture relief is supported to foundation.
Overhead door/window heads are omitted to keep door passages open and avoid
unsupported miniature bridges. The predecessor display's gym bleachers and
patio free-edge guards remain omitted; patio platform remains included.
These are adapted display models, with fine details approximated at scale.
Original native/Blender files and original P01 delivered files are preserved.

ASSEMBLY AND PROJECTION
Assembly_Registration_1_1.svg is an actual-size north-up reference; do not
use Fit to page when printing it. It includes original architectural corner
landmarks and added H01/H02 accessory centres. Calibration_Landmarks.json
retains original P01 architectural witnesses. Manifest records inverse
per-plate transforms; no new connector keys are required.
Assembled OBJ/MTL: Z-up millimetres, normals, unchanged planar UVs, three
named groups. Projection data uses the unchanged predecessor 1:100 canvas
and source origin. PNG rows increase south/down; OBJ v increases north/up.
Height PNG unsigned16 values encode 0.01 mm. NPZ material IDs:
0 background, 1 Opaque, 2 Glazing, 3 HangingLoops (same filament as 2).
Architectural_projection_receiver_mask excludes top-visible accessories;
captured roots under white floor do not remove that floor from the mask.
Recalibrate your physical projector for the new print scale. No physical
projector calibration is claimed. Inherited room metadata is reference only.

VALIDATION
Closed material bodies, STL/3MF reloads and fused combined reference pass
watertightness, winding and edge checks. Pairwise material overlap is zero.
Tile material volumes sum to the assembly. Exactly two base materials and
Loop extruder 2 assignments are checked in serialized 3MF files. All seven
walls pass 41 location probes; three door witnesses stay open. Eyelet bores
are void and both captures restrain 2 mm lift/outward test displacements.
Capture tests measure geometry only. Copied native source hashes are intact.
Actual_Geometry_Oblique.png and Actual_Geometry_Six_Tile_Layout.png show the
delivered meshes; cyan identifies transparent material, not optical realism.
No actual slice preview, physical print, load test or optical test is claimed.
