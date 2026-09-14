import bpy, pathlib, json, hashlib
R=pathlib.Path(__file__).parent
s=bpy.context.scene
assert s.camera.data.type=='ORTHO'
assert all(abs(v)<1e-7 for v in s.camera.rotation_euler)
assert (s.render.resolution_x,s.render.resolution_y,s.frame_start,s.frame_end,s.render.fps)==(1024,786,1,144,24)
assert not s.camera.data.dof.use_dof
assert not [o for o in s.objects if o.type=='LIGHT' and not o.hide_render]
missing=[]
for im in bpy.data.images:
    if im.source=='SEQUENCE':
        for i in range(1,25):
            if not (R/'imagegen_raw'/f'people_{i:04}.png').is_file():missing.append(f'people_{i:04}.png')
    elif im.source=='FILE' and not im.packed_file and not pathlib.Path(bpy.path.abspath(im.filepath)).is_file():missing.append(im.filepath)
assert not missing,missing
actors=[o for c in bpy.data.collections if c.name.startswith('STUDENTS - ') for o in c.objects]
assert len(actors)==93
moving=actors+[bpy.data.objects['Basketball pass']]
s.frame_set(1);bpy.context.view_layer.update()
a={o.name:o.matrix_world.copy() for o in moving}
s.frame_set(145);bpy.context.view_layer.update()
error=max(abs(o.matrix_world[i][j]-a[o.name][i][j]) for o in moving for i in range(4) for j in range(4))
assert error<.0001,error
for frame in [1,109,145]:
    s.frame_set(frame)
    s.render.filepath=str(R/f'reopened_frame_{frame:04}.png')
    bpy.ops.render.render(write_still=True)
for o in moving:o.hide_render=True
s.frame_set(1)
s.render.filepath=str(R/'Projection_Base_Playback.png')
bpy.ops.render.render(write_still=True)
source=pathlib.Path(json.loads((R/'render_contract.json').read_text())['source'])
h=hashlib.sha256(source.read_bytes()).hexdigest()
assert h==json.loads((R/'render_contract.json').read_text())['source_sha256']
(R/'scene_validation.json').write_text(json.dumps({'status':'passed','scene':bpy.data.filepath,'camera':'ORTHO vertical','resolution':[1024,786],'frames':[1,144],'fps':24,'missing_images':missing,'student_count':len(actors),'visible_lights':0,'loop_transform_max_error':error,'reopened_render_frames':[1,109,145],'source_unchanged':True},indent=2))
print('SCENE_VERIFIED',error)
