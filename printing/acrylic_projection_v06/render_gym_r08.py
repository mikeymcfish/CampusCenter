from pathlib import Path
import bpy,shutil,hashlib,json
R=Path(__file__).parent
source=R/'Source_Studio.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
backup=R/'revision_08_before/rooms/GYM';backup.mkdir(parents=True,exist_ok=True)
for p in (R/'rooms/GYM').glob('*.png'):shutil.copy2(p,backup/p.name)
bpy.ops.wm.open_mainfile(filepath=str(source))
hidden=[]
for o in bpy.context.scene.objects:
    if 'bleacher' in o.name.lower():o.hide_render=True;hidden.append(o.name)
assert len(hidden)>=6
code=(R/'render_rooms.py').read_text()
code=code.replace("pilot='--pilot' in sys.argv", "rooms=[r for r in rooms if r['number']=='GYM']\npilot=False")
code=code.replace("if not pilot:bpy.ops.wm.save_as_mainfile(filepath=str(R/'Ground_Room_Render_Setup.blend'))", "")
code=code.replace("'render_report.json'", "'gym_r08_render_report.json'")
exec(compile(code,str(R/'render_rooms.py'),'exec'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(R/'rooms/GYM/r08_render.json').write_text(json.dumps({'source_unchanged_sha256':before,'hidden_bleachers':hidden,'print_reference_only':True},indent=2))
