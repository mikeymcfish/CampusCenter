import bpy,pathlib,json,time,sys
R=pathlib.Path(__file__).parent;s=bpy.context.scene
preview='--preview' in sys.argv;folder=R/('previews' if preview else 'stills');folder.mkdir(exist_ok=True)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU';s.cycles.samples=32 if preview else 256;s.cycles.adaptive_threshold=.04 if preview else .01
s.render.resolution_x=960 if preview else 1920;s.render.resolution_y=540 if preview else 1080;s.render.resolution_percentage=100
results=[]
for name in ['01_Entrance','02_Commons','03_iLab']:
 s.camera=bpy.data.objects[name];s.frame_set(1);s.render.image_settings.media_type='IMAGE' if preview else 'MULTI_LAYER_IMAGE';s.render.image_settings.file_format='OPEN_EXR_MULTILAYER' if not preview else 'PNG';s.render.image_settings.color_depth='16' if not preview else '8';s.render.image_settings.color_mode='RGBA' if not preview else 'RGB'
 if not preview:s.render.image_settings.exr_codec='ZIP'
 s.render.filepath=str(folder/(name+('.png' if preview else '.exr')));start=time.perf_counter();bpy.ops.render.render(write_still=True);elapsed=time.perf_counter()-start
 if not preview:
  s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='16';bpy.data.images['Render Result'].save_render(str(folder/(name+'.png')),scene=s)
 row={'camera':name,'seconds':elapsed,'resolution':[s.render.resolution_x,s.render.resolution_y],'max_samples':s.cycles.samples,'adaptive_threshold':s.cycles.adaptive_threshold,'engine':'Cycles','device':'CUDA','preview':preview}
 results.append(row);(folder/'timings.json').write_text(json.dumps(results,indent=2));print('SHOT_DONE',json.dumps(row),flush=True)
(folder/'complete.json').write_text(json.dumps({'outputs':results,'status':'rendered'},indent=2))


