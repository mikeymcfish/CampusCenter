from pathlib import Path
import json,shutil,html
R=Path(__file__).parent;ROOT=R.parent;D=R/'print'
s=(ROOT/'projection_furnished_v04/export_cad.py').read_text().replace("R=Path(__file__).parent;sys.path.insert(0,str(R.parent/'tmp/cadpackages'))","R=Path(__file__).parent/'print';sys.path.insert(0,str(R.parent.parent/'tmp/cadpackages'))")
s=s.replace('Campus_Center_Ground_Furnished_1_87p5.step','Campus_Center_Ground_Acrylic_1_87p5.step');(R/'export_cad.py').write_text(s)
s=(ROOT/'projection_enclosed_v05/render_ground.py').read_text().replace("R=pathlib.Path(__file__).parent/'ground'","R=pathlib.Path(__file__).parent/'print'").replace('Campus_Center_Ground_Enclosed_1_87p5.stl','Campus_Center_Ground_Acrylic_1_87p5.stl')
s=s.replace("s.cycles.samples=24","s.cycles.samples=32")
s=s.replace("s.cycles.device='CPU'","prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices();[setattr(d,'use',d.type=='CUDA') for d in prefs.devices];s.cycles.device='GPU'")
# The calibrated masks are rendered without panes: clear acrylic is not a receiving surface.
s=s.replace("print('PRINT_AND_MASKS_RENDERED',flush=True)",'''print('PRINT_AND_MASKS_RENDERED',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'Campus_Center_Furnished_Print.blend'))
s=bpy.context.scene
bpy.ops.wm.stl_import(filepath=str(R/'Acrylic_Panes_Reference_ONLY.stl'))
pane=bpy.context.object;pane.name='Clear acrylic inserts - reference only';pane.scale=(.001,)*3
mat=bpy.data.materials.new('Clear acrylic demonstration');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.65,.90,.95,1);p.inputs['Roughness'].default_value=.12;p.inputs['Transmission Weight'].default_value=.85;p.inputs['IOR'].default_value=1.49;pane.data.materials.append(mat)
s.render.filepath=str(R/'Acrylic_Installed_Preview.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Acrylic_Assembly_Reference.blend'))
''')
(R/'render_print.py').write_text(s)
from print_edits_r08 import update_height_data
update_height_data(ROOT,D)
rows=json.loads((D/'glazing_schedule.json').read_text());sheets=[];cuts=[];labels=[];x=y=10.;rowh=0
def save():
 if not cuts:return
 n=len(sheets)+1;p=D/f'Acrylic_Cut_Sheet_{n:02d}.svg'
 p.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="610mm" height="305mm" viewBox="0 0 610 305"><g id="CUT" fill="none" stroke="#ff0000" stroke-width="0.05">'+''.join(cuts)+'</g><g id="LABELS_HIDE_BEFORE_CUTTING" font-family="sans-serif" font-size="3" fill="#000000">'+''.join(labels)+'</g></svg>');sheets.append(p.name)
for q in rows:
 w=q['cut_width_mm'];h=q['cut_height_mm']
 if x+w>600:x=10;y+=rowh+9;rowh=0
 if y+h>295:save();cuts=[];labels=[];x=y=10;rowh=0
 cuts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}"/>');labels.append(f'<text x="{x:.3f}" y="{y-2:.3f}">{q["id"]}</text>');q.update(cut_sheet=len(sheets)+1,cut_x_mm=x,cut_y_mm=y)
 x+=w+8;rowh=max(rowh,h)
save();(D/'glazing_schedule.json').write_text(json.dumps(rows,indent=2))
(D/'README.md').write_text('''# Ground floor with acrylic glazing — v06

Scale 1:87.5. STL, STEP, 3MF and SVG units are millimetres. Print the six individual `print_tiles` files at 100%, flat on their supplied Z=0 underside. No supports are needed by the geometry checks; slicer and physical print checks still apply.

## Acrylic

Use nominal **1/16 inch (1.5875 mm) clear acrylic**. Commercial sheet may be sold as 0.060 inch / 1.5 mm and actual thickness varies. The channels are **1.85 mm wide**, with 2.4 mm bottom engagement. The alternate 1/18 inch thickness is 1.4111 mm and would fit more loosely in these channels.

Print `Acrylic_Fit_Coupon` first. With the open ends facing you and its long side horizontal, the five slots from left to right are 1.65, 1.75, **1.85**, 1.95 and 2.05 mm. Test a small offcut of your actual sheet. If the 1.85 mm channel is too tight or loose, update SLOT in the editable build script and regenerate; do not scale the whole model to adjust the channel.

The CSV and SVG cut sheets specify finished rectangular insert sizes. SVG sheets are 610 x 305 mm, at 1:1 size. CUT contains outlines; hide LABELS_HIDE_BEFORE_CUTTING when cutting. Apply the kerf correction appropriate to your machine and material. Do not resize to fit a page. Keep IDs with the pieces until assembly.

Insert each pane vertically from above into the base groove and the two side grooves. The frames have no bridging top rail, so the print remains support-free and panes remain removable. Sills and door-light heights follow the source glazing; the omitted top rails are a print adaptation. Small mullions are thickened for strength. Split glazing runs at print seams use separate panes, so an insert does not bridge two tiles.

`Acrylic_Panes_Reference_ONLY.stl` is a visual assembly reference, NOT a file to print in white. The clear sheets are the actual glazing. `Campus_Center_Acrylic_Assembly_Reference.blend` shows the inserted panes. Architectural windows and glazed door lights are included; equipment lids/display cases and stair/patio guardrails are not windows and remain as previously modeled.

## Assembly and projection

Use the same A1–A3 south / B1–B3 north arrangement as v05. The assembly 3MF preserves the global positions; individual tile files are for printing. Align and butt-join seams on a flat surface. No supplemental ground board, stacking pins, or floating furniture were added.

The print grows less than 1 mm in overall X because of strengthened window frames. The overhead canvas remains 830 x 637.08984375 mm, center XY 398 / 289 mm. Use the regenerated v06 receiver masks and artwork. Clear acrylic is intentionally excluded from projection receiving surfaces; real acrylic edges can still catch light and should be checked during physical calibration.

This revision is a display model, not a construction drawing. Geometry and insertion checks are recorded in print_validation.json. Actual printer fit and projector alignment have not been physically tested.
''',encoding='utf-8')
print('PRINT_SCRIPTS_READY',len(sheets),'cut sheets')
