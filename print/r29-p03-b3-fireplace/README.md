# P03 fireplace correction - B3 tile only

[Download Ground_R29_P03_Tile_B3_1_100_Fireplace.3mf](https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-print-p03-b3-fireplace-20261006/Ground_R29_P03_Tile_B3_1_100_Fireplace.3mf) (159,626 bytes).

Replace only `Ground_R29_P02_Tile_B3_1_100.3mf` from the P02 six-tile 1:100 set with this file. Open the corrected 3MF in your slicer and retain its placement, scale, rotation and material assignments. All other P02 tiles, including B2 hanging loops, stay as supplied. This is a single-tile replacement, not a revised complete print package; the P02 release and history are preserved.

An exclusion matching the substring `fire` unintentionally omitted physical fireplace actors. This correction restores nine native R29 actors, including the surround, hearth, firebox and real logs. The chimney retains the existing ground-floor/open-roof cut; no flame or particle geometry is invented. The opaque body is closed and connected; glazing is unchanged, with no material overlap. Software seam/placement checks and H2D static fit passed, and native geometry was visually reviewed. Actual slicing, purge-tower dimensions and physical print/fit are **untested**.

**Projection receiver update pending:** existing P02 UV01 receivers and P01 media do not include the added fireplace surfaces. A matched receiver/UV update and calibration review are required before claiming full projection alignment. Current receiver/media files remain unchanged.

SHA-256: `0873b4f30cebc013c030a0a0ac1f7b1f715ca4463ce551101e1668a91a2293ad`. The release file is byte-identical to the validated producer handoff. QA here has private provenance paths reduced to basenames and Library metadata removed. No build, geometry edit or whole-package rewrite was performed for publication.
