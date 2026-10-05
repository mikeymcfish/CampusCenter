CampusCenter physical P02 - MadMapper model/UV preparation UV01
SOURCE: Ground_R29_P02_Sample_1_250.obj
SCALE: actual P02 physical 1:250 source, NOT a rescaled other model.
BOUNDS: [[4.48, 2.72, 0.0], [267.84, 199.52, 19.0688]] mm. DIMENSIONS: [263.35999999999996, 196.8, 19.0688] mm.
XYZ right-handed, Z up, +Y north; origin and all relative positions retained.

GEOMETRY
33708 source vertices / 67120 triangles retained.
Final OBJ contains the EXACT original decimal v/vn strings and indexed face
winding; only vt/corner UV references change. No physical geometry repair was
needed. P02 print adaptations, repaired gym walls and pane thickness stay.
This actual sample source has no eyelets; none were added.
No original P02 file or working Blender source was saved or changed.
Internal contacts between closed material bodies are intentional; see
Geometry_Surface_Contact_Audit.json. No surfaces were silently removed.

ATLAS AND CONTROL
Use CampusCenter_P02_Sample_1_250_UV01.obj together with its MTL and Atlas_Diagnostic.png.
The editable CampusCenter_P02_Sample_1_250_UV01.blend has a packed diagnostic image, one UV layer,
and FACE integer surface_id attributes matching Surface_Lookup_Manifest.json.
One 8192x8192 atlas has 14652 independent charts; opposite wall sides
are separate UV regions. All triangles have positive unmirrored UV area,
including float32 UVs. Zero positive-area triangle overlaps within charts,
and disjoint chart rectangles across the atlas. Charts have 4px padding
(8px separation) and minimum 2px spans at 8192. PNG rows run downward;
OBJ UV v runs upward. Masks and textures use this same new atlas convention.

Material names ALONE do not create independent MadMapper controls. Compose
the input image/video in this atlas using separate room or surface layers.
Room_IDs_uint8.png + Room_ID_Lookup.json identify room candidates. Provided
room_masks/*.png select all parts for each room candidate. Surface_IDs_uint16
stores exact numeric surface IDs; CSV/JSON lookup records source face indices,
roles, part, facing UV basis, bounding rectangle and texel density. Multiple
charts can belong to one room; combine their masks for one room control.
Individual wall-side controls use their unique surface IDs, not shared slots.
Apply Default_Opaque_Receiver_Mask.png to keep content off glazing, eyelets
and downward/underside faces. Separate Opaque/Glazing/HangingLoops masks
allow deliberate alternatives. Geometry stays present when masked out.
Begin with Atlas_Diagnostic.png; room colours, checkers, labels and +U arrows
help expose side assignment, flips and stretch. UV_Wireframe_Transparent.png
has a genuinely transparent background. Room_Atlas_Index.png provides a
readable name/index guide; the full-size reference allows detailed zoom.
Do not use the old P02 top-plan textures with these replacement UVs directly.
Old textures need an explicit remap into the new atlas.

ROOM REVIEW
A101 room numbers/names are reference labels, not newly asserted R29 room
boundaries. Gym interior limits are directly verified from native P02 walls.
Other room candidates use inherited registered A101 boxes. Review corridor
131 (absent from that metadata), stair A/B assignments, R25 revised room
boundaries, and open Commons/cafe/display-hall boundaries. Neutral EXTERIOR
IDs retain unassigned faces. Room_Review_Map.png in the shared reference set
shows registered A101 reference points on actual 1:100 physical geometry.
No uncertain new room names were invented. Renaming labels does not require
changing the physical model; boundary corrections require updating masks/UV
sector assignments and validating again.

METRIC STRETCH AND FRESH IMPORT
Exact OBJ geometry comparison passes; fresh Blender native OBJ import in an
empty scene uses forward Y / up Z / scale 1.0. Scene display units are mm,
scale_length=0.001; no model transform is applied. All object matrices are
identity. Triangle order/count/winding and each UV corner are checked.
Maximum Blender coordinate storage error: 0.000014989 mm.
Maximum UV storage error: 0.000244141 pixels at 8192.
Minimum imported-normal dot source: 0.999827406; no normals are flipped.
The OBJ is the authoritative exact decimal model. Blender float32 storage
and custom-normal encoding introduce these measured small differences.
Re-export after editing must be compared again; source-exactness does not
automatically extend to a future Blender export.
Area-weighted 95th-percentile stretch ratio: 1.003195.
Surface-area fraction above 2x anisotropy: 0.015410%.
The maximum is much larger for microscopic/narrow source charts expanded
to the minimum 2px span; inspect the full metrics and checker diagnostic.
This UV-only expansion does not alter their physical dimensions.
Actual NorthEast/SouthEast diagnostic PNGs render the fresh imported OBJ.
Keep atlas resolution/padding in mind when downsampling content.

CALIBRATION AND LIMITS
Retain the source coordinates. Shared physical calibration landmarks are
included verbatim for 1:100. The separate sample is the actual 1:250 P02
sample with its own relief/foundation adaptation and its own UV atlas.
Never substitute one physical scale for the other. Recheck axis conventions
and corresponding physical points when importing into MadMapper; match
the model to the real projector/printed assembly. UV content changes even
though the physical model frame is unchanged. Verify current room masks
before using them as show controls. No MadMapper project, animation, cue,
software installation or physical projector calibration is supplied/claimed.
MadMapper was not run; OBJ compatibility follows standard Wavefront v/vt/vn
and official 3D OBJ import support, tested here with fresh Blender import.
Official references:
https://docs.madmapper.com/madmapper/6/4.-surfaces/advanced-3d-and-scanning
https://madmapper.com/files/01-Introduction%20to%20the%20User%20Interface.pdf
