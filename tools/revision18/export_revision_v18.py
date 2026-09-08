from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).parent;O=R/'output_v18';src=O/'Campus_Center_Textured.blend';bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
info={'blender':bpy.app.version_string,'objects':len(s.objects),'students':len([o for o in s.objects if o.name.startswith('Student_')]),'frames':s.frame_end,'fps':s.render.fps,'packed_images':[i.name for i in bpy.data.images if i.packed_file],'missing_images':[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).exists()],'armatures':len([o for o in s.objects if o.type=='ARMATURE'])}
assert info['students']==112 and not info['missing_images'] and len(info['packed_images'])>=8
bpy.ops.export_scene.gltf(filepath=str(O/'Campus_Center_Textured.glb'),export_format='GLB',export_animations=False,export_cameras=True,use_renderable=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'Campus_Center_Textured.glb'))
info['glb_reopened']=True;info['glb_meshes']=len([o for o in bpy.context.scene.objects if o.type=='MESH']);info['glb_students']=len([o for o in bpy.context.scene.objects if o.name.startswith('Student_')]);info['glb_images']=len([i for i in bpy.data.images if i.source=='FILE']);assert info['glb_students']==112 and info['glb_images']>=8
old=json.loads((O/'changes.json').read_text());assert hashlib.sha256(Path(old['source']).read_bytes()).hexdigest()==old['source_sha256'];info['original_preserved']=True
for ext in ['blend','glb']:
 p=O/('Campus_Center_Textured.'+ext);info[ext+'_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(O/'reopen_validation.json').write_text(json.dumps(info,indent=2));print('V18_EXPORT_REOPEN_OK',flush=True)
