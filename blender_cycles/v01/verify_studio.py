import bpy,pathlib,json,hashlib
R=pathlib.Path(__file__).parent;s=bpy.context.scene
original=json.loads((R/'preflight.json').read_text());report={'file':bpy.data.filepath,'engine':s.render.engine,'samples':s.cycles.samples,'resolution':[s.render.resolution_x,s.render.resolution_y],'camera_names':[],'missing_images':[],'packed_file_images':0,'mesh_count':sum(o.type=='MESH' for o in s.objects),'source_mesh_count':original['meshes'],'walkthrough_retained':False}
for name in ['01_Entrance','02_Commons','03_iLab']:
 assert name in bpy.data.objects;report['camera_names'].append(name)
walk=bpy.data.objects.get(original['camera']);report['walkthrough_retained']=bool(walk and walk.animation_data)
for im in bpy.data.images:
 if im.source=='FILE':
  if im.packed_file:report['packed_file_images']+=1
  elif not pathlib.Path(bpy.path.abspath(im.filepath)).exists():report['missing_images'].append(im.name)
report['source_unchanged']=hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest()==original['sha256']
assert report['source_unchanged'] and not report['missing_images'] and report['mesh_count']==report['source_mesh_count']
assert report['engine']=='CYCLES' and report['samples']==256 and report['resolution']==[1920,1080]
assert report['walkthrough_retained']
report['status']='passed';(R/'scene_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
