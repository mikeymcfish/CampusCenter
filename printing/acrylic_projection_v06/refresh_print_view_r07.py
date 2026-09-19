from pathlib import Path
import shutil,hashlib,json
R=Path(__file__).parent
source=R/'print/Campus_Center_Projection_Receiver.blend'
working=R/'revision_07_before/Projection_Receiver_Working.blend'
shutil.copy2(source,working)
before=hashlib.sha256(source.read_bytes()).hexdigest()
code=(R/'render_projection_views.py').read_text()
code=code.replace("R/'print/Campus_Center_Projection_Receiver.blend'","R/'revision_07_before/Projection_Receiver_Working.blend'")
code=code.replace("[('Ink_Map','assets/Ink_Map.png'),('Depth_Contours','examples/Depth_Contours_Preview.png'),('Surface_Ripples','examples/Surface_Ripples_Preview.png'),('Explorer','examples/Explorer_Preview.png')]","[('Explorer','examples/Explorer_Preview.png')]")
code=code.replace("bpy.ops.wm.save_as_mainfile(filepath=str(R/'Projection_Review.blend'))", "")
exec(compile(code,str(R/'render_projection_views.py'),'exec'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(R/'projection/review/r07_validation.json').write_text(json.dumps({'source':str(source),'source_sha256_unchanged':before,'working_copy':str(working),'output':'Explorer_On_Print.png','resolution':[1600,1200],'samples':64,'device':'CUDA','purpose':'Existing print presentation refreshed with cinematic gym photo'},indent=2))
