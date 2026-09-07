# Editable laser-kit source

Use a separate copy of this directory when changing the design. Python 3.11 or newer is recommended.

```
python -m pip install -r requirements.txt
```

Edit `output_v13_laser/config.json`, then run from this directory:

```
python build_laser_v13.py
python audit_laser_v13.py
python create_laser_guide_v13.py
```

The builder reads the included architectural geometry and stair connection data. Outputs go into this directory's `output_v13_laser` folder. The audit must report zero errors before fabrication.

For fit calibration, the approximate kerf is measured material thickness plus desired clearance minus the preferred raw coupon-slot width. Confirm any revised settings with another test cut. Supplied defaults are 3.175 mm material, 0.15 mm kerf and 0.05 mm clearance.

The standalone coupon uses raw, uncompensated slot widths. `finish_laser_v13.py` exports it and also creates a source bundle; running that script repeatedly inside this bundle is unnecessary.

The guide's maps and inventory follow generated geometry, but descriptive text and the supplied assembly preview images document the original 1:200 configuration. If you change thickness, scale, kerf or piece counts, review and update guide text and previews before distributing it. The included Blender file in the parent kit is the assembled original configuration, not a live parametric link.
