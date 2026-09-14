import bpy,pathlib,json,math,hashlib
R=pathlib.Path(__file__).parent;s=bpy.context.scene
assert s.camera.data.type=='ORTHO';assert all(abs(v)<1e-7 for v in s.camera.rotation_euler)
assert (s.render.resolution_x,s.render.resolution_y,s.frame_start,s.frame_end,s.render.fps)==(1024,786,1,24,4)
assert not s.camera.data.dof.use_dof;assert not [o for o in s.objects if o.type=='LIGHT' and not o.hide_render]
missing=[]
for im in bpy.data.images:
 if im.source=='SEQUENCE':
  for i in range(1,25):
   p=R/'imagegen_raw'/f'people_{i:04}.png'
   if not p.is_file():missing.append(str(p))
 elif im.source=='FILE' and not im.packed_file and not pathlib.Path(bpy.path.abspath(im.filepath)).is_file():missing.append(im.filepath)
assert not missing,missing
actors=list(bpy.data.collections['IMAGEGEN PEOPLE - disable to show base only'].objects)
assert len(actors)==4
s.frame_set(1);bpy.context.view_layer.update();a={o.name:o.matrix_world.copy() for o in actors}
s.frame_set(25);bpy.context.view_layer.update();error=max(abs(o.matrix_world[i][j]-a[o.name][i][j]) for o in actors for i in range(4) for j in range(4));assert error<.0001,error
s.frame_set(1);s.render.filepath=str(R/'reopened_frame_0001.png');bpy.ops.render.render(write_still=True)
s.frame_set(19);s.render.filepath=str(R/'reopened_frame_0019.png');bpy.ops.render.render(write_still=True)
source=R.parent/'projection_print_v01/Campus_Center_Projection.blend';h=hashlib.sha256(source.read_bytes()).hexdigest();assert h==json.loads((R/'render_contract.json').read_text())['source_sha256']
(R/'scene_validation.json').write_text(json.dumps({'status':'passed','scene':bpy.data.filepath,'camera':'ORTHO vertical','resolution':[1024,786],'frames':[1,24],'fps':4,'missing_images':missing,'people_collection_count':len(actors),'visible_lights':0,'loop_transform_max_error':error,'reopened_render_frames':[1,19],'source_unchanged':True},indent=2))
print('SCENE_VERIFIED',error)
