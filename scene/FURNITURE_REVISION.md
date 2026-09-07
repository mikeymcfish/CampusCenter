# Furniture and fixtures - revision 15

Source: `references/plans/MEP_Progress_2025-08-20.pdf`, principally page 12 E-102, with plumbing positions and fixture types from page 1 P-100. Page 14 E-105 was checked against the existing iLab equipment. The newer architectural shell and the user's printer/sink/spray-booth changes take precedence over older underlays and room numbers.

Added or corrected:
- Commons curved lounge, lounge-chair groups, round dining tables, two four-seat rectangular tables, long collaboration table and stools. Conflicting old west-wall bench removed; perimeter seating retained on the north wall.
- Cafe: two tablet POS stands, two refrigerated displays, turbo oven, coffee machine, under-counter refrigerator and ice machine, sink and point-of-use water heater.
- Locker rooms: 130 columns / 260 two-tier doors per room, 15-inch pitch, double-sided islands and return banks. Door pulls, labels and vents are geometry.
- Men's toilet: two urinals and one WC. Lavatories face the shared wet wall. Mirrors, dispensers, traps, privacy doors and grab bars added.
- Four showers: supply/mixer fittings, shower heads, drains, privacy returns and gathered curtains.
- Two fountain/bottle-fill stations: Boolean-cut wall recesses beside the gym/locker corridor and innovation lab/stair A. Recesses verified by ray tests against actual wall geometry.
- Athletics visitor table/chairs and ice maker, laundry pair and blank information displays.
- Ceiling projector and motorized-screen cassette. Enable **AV - LOWERED SCREEN - toggle** in the Blender Outliner to show the blank lowered screen. Disable **AV - ceiling projector and cassette** to hide the AV hardware too.

All materials remain texture-free. Product shapes, furniture dimensions, AV suspension heights and locker return distribution are representative interpretations where detail is not specified. Existing classroom, office and iLab furniture remains where this PDF does not provide a replacement arrangement. This is a visual model, not a coordinated fabrication or plumbing design.

The Blender screen starts hidden. The static GLB includes the optional screen as named geometry; hide that node in an importer if desired. Camera animation is retained in Blender. No new walkthrough video was rendered.

Validation: Blender and GLB reopened; 112 students retained; zero texture nodes; two POS stands; two refrigerated displays; two verified wall recesses. No collisions found between sampled walking positions and new furniture. Seventeen mannequins were moved clear of the new furniture. See `reopen_validation.json` and review images.
