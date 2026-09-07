# Campus Center laser-cut kit

Two 12 x 24 inch sheets, 1:200 scale, nominal 1/8 inch (3.175 mm) plywood. Includes the two floors, walls and stairs; no roof. There are 157 numbered pieces, including the two test-fit coupon pieces.

Start with `Test_Fit_Coupon.svg` or `.dxf`, then follow the 24-page `Campus_Center_Laser_Assembly_Guide.pdf`. The coupon is also included on the full sheet layouts; do not count the standalone coupon as additional model parts.

## Test the fit first

The current model cut paths already compensate for an assumed 0.15 mm kerf and provide 0.05 mm joint clearance. Do not apply a second kerf offset in laser software. Import at 100% in millimeters; each sheet is 609.6 x 304.8 mm.

The coupon slots are deliberately uncompensated. Insert the thickness edge of the tongue into each slot. Slot 6 (3.075 mm raw path width) corresponds to the supplied settings. If it does not give a comfortable slip fit, measure your material, adjust the source configuration and regenerate before cutting the full sheets. Do not force narrow tabs.

## Operations and assembly

- CUT: red closed vector contours.
- ENGRAVE: blue detail vectors.
- LABELS: gray single-stroke vector numbers, on a separate layer that can be hidden or disabled.

Engrave first, then cut internal openings before outside outlines. Select power and speed for your own machine and plywood. Glue tab-and-slot floor connections and wall butt joints. Stair profiles are laminated in numbered pairs. Assemble the upper floor separately; it rests on the ground-floor walls. The tall gym walls remain attached to the ground floor.

## Files

- Sheet_01/02_12x24.svg and .dxf: full-size layouts, with separate operation layers.
- Test_Fit_Coupon.svg and .dxf: standalone material-fit test.
- Campus_Center_Laser_Assembly_Guide.pdf: numbered plans, joints, stairs, stacking, sheet maps and inventory.
- Campus_Center_Laser_Assembly.blend and preview PNGs: assembled geometry and visual reference.
- parts_list.csv, parts_manifest.json, config.json and audit.json: inventory, geometry, settings and digital checks.
- editable_source/: scripts and source geometry for adjustment.

The contours, sheet bounds, wall overlaps, floor-slot clearances and vector labels were digitally checked, and the assembled preview and PDF were visually reviewed. This kit has not been physically cut or assembled. The plywood thickness requires simplified architectural details; it is a scale display model.
