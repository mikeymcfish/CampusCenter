import bpy,pathlib,json,sys,time
R=pathlib.Path(__file__).parent;s=bpy.context.scene;preview='--preview' in sys.argv
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU';s.render.image_settings.color_mode='RGBA';s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
out=R/'projection';out.mkdir(exist_ok=True);t=time.time()
shells=[o for o in s.objects if o.name.startswith('Receiver ')];visibility={o.name:o.hide_render for o in s.objects}
for o in s.objects:
 if o.type in {'MESH','CURVE','FONT','EMPTY'}:o.hide_render=o not in shells
oldindices={o.name:[p.material_index for p in o.data.polygons] for o in shells};oldmats={o.name:list(o.data.materials) for o in shells};m=bpy.data.materials.new('Calibration emission');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(1,1,1,1);outnode=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],outnode.inputs[0])
for o in shells:o.data.materials.clear();o.data.materials.append(m)
s.cycles.samples=8;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.frame_set(1);s.render.filepath=str(out/'receiver_mask.png');bpy.ops.render.render(write_still=True)
geo=nt.nodes.new('ShaderNodeNewGeometry');checker=nt.nodes.new('ShaderNodeTexChecker');checker.inputs['Scale'].default_value=1/2.1875;checker.inputs['Color1'].default_value=(.08,.18,.8,1);checker.inputs['Color2'].default_value=(.95,.95,.95,1);nt.links.new(geo.outputs['Position'],checker.inputs['Vector']);nt.links.new(checker.outputs['Color'],em.inputs[0]);s.render.filepath=str(out/'calibration_25mm.png');bpy.ops.render.render(write_still=True)
for o in shells:
 o.data.materials.clear()
 for mat in oldmats[o.name]:o.data.materials.append(mat)
 for p,idx in zip(o.data.polygons,oldindices[o.name]):p.material_index=idx
for o in s.objects:o.hide_render=visibility[o.name]
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.cycles.samples=16 if preview else 24
if preview:
 for frame in [1,37,73,109]:s.frame_set(frame);s.render.filepath=str(out/f'preview_{frame:04}.png');bpy.ops.render.render(write_still=True)
else:
 frames=out/'frames';frames.mkdir(exist_ok=True)
 for frame in range(1,s.frame_end+1):
  s.frame_set(frame);s.render.filepath=str(frames/f'{frame:04}.png');bpy.ops.render.render(write_still=True);print('FRAME_DONE',frame,flush=True)
 (out/'render_complete.json').write_text(json.dumps({'frames':s.frame_end,'seconds':time.time()-t,'resolution':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps}))
