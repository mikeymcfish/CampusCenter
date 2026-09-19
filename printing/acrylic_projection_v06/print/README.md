# Ground floor with acrylic glazing â€” v06

Scale 1:87.5. STL, STEP, 3MF and SVG units are millimetres. Print the six individual `print_tiles` files at 100%, flat on their supplied Z=0 underside. No supports are needed by the geometry checks; slicer and physical print checks still apply.

## Acrylic

Use nominal **1/16 inch (1.5875 mm) clear acrylic**. Commercial sheet may be sold as 0.060 inch / 1.5 mm and actual thickness varies. The channels are **1.85 mm wide**, with 2.4 mm bottom engagement. The alternate 1/18 inch thickness is 1.4111 mm and would fit more loosely in these channels.

Print `Acrylic_Fit_Coupon` first. With the open ends facing you and its long side horizontal, the five slots from left to right are 1.65, 1.75, **1.85**, 1.95 and 2.05 mm. Test a small offcut of your actual sheet. If the 1.85 mm channel is too tight or loose, update SLOT in the editable build script and regenerate; do not scale the whole model to adjust the channel.

The CSV and SVG cut sheets specify finished rectangular insert sizes. SVG sheets are 610 x 305 mm, at 1:1 size. CUT contains outlines; hide LABELS_HIDE_BEFORE_CUTTING when cutting. Apply the kerf correction appropriate to your machine and material. Do not resize to fit a page. Keep IDs with the pieces until assembly.

Insert each pane vertically from above into the base groove and the two side grooves. The frames have no bridging top rail, so the print remains support-free and panes remain removable. Sills and door-light heights follow the source glazing; the omitted top rails are a print adaptation. Small mullions are thickened for strength. Split glazing runs at print seams use separate panes, so an insert does not bridge two tiles.

`Acrylic_Panes_Reference_ONLY.stl` is a visual assembly reference, NOT a file to print in white. The clear sheets are the actual glazing. `Campus_Center_Acrylic_Assembly_Reference.blend` shows the inserted panes. Architectural windows and glazed door lights are included; equipment lids/display cases and stair guardrails are not windows. The patio enclosure is removed in r08.

## Assembly and projection

Use the same A1â€“A3 south / B1â€“B3 north arrangement as v05. The assembly 3MF preserves the global positions; individual tile files are for printing. Align and butt-join seams on a flat surface. No supplemental ground board, stacking pins, or floating furniture were added.

The print grows less than 1 mm in overall X because of strengthened window frames. The overhead canvas remains 830 x 637.08984375 mm, center XY 398 / 289 mm. Use the regenerated v06 receiver masks and artwork. Clear acrylic is intentionally excluded from projection receiving surfaces; real acrylic edges can still catch light and should be checked during physical calibration.

This revision is a display model, not a construction drawing. Geometry and insertion checks are recorded in print_validation.json. Actual printer fit and projector alignment have not been physically tested.

## r08 print correction

The innovation-lab patio is open at its free edges. Its platform and adjacent building walls are preserved. Both three-row gym bleacher banks are removed. All six print tiles remain single connected, watertight solids, with no elevated downward-facing faces. The scale, assembly registration, 40 acrylic pane dimensions and 1.85 mm slots remain unchanged. Updated masks, previews and projection videos match this geometry. The full architectural Blender source remains unchanged.
