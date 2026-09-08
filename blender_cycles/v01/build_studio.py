import bpy,pathlib,json,math,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).parent;s=bpy.context.scene
source_hash=hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest()
contract={'source':'P:/_code/CampusCenter/scene/Campus_Center_Current.blend','source_sha256':source_hash,'working_file':'Campus_Center_Cycles_Studio.blend','blender':bpy.app.version_string,'engine':'Cycles','device':'RTX 4090 CUDA GPU only','final_samples':256,'adaptive_threshold':.01,'denoiser':'OpenImageDenoise','resolution':[1920,1080],'preview_resolution':[960,540],'preview_samples':32,'frame':1,'outputs':['01_Entrance.png','02_Commons.png','03_iLab.png'],'supplemental_outputs':['01_Entrance.exr','02_Commons.exr','03_iLab.exr'],'png':'16-bit RGB AgX','exr':'16-bit multilayer linear ZIP','passes':['Combined','Denoising Normal','Denoising Albedo','Depth','Normal','Diffuse Direct','Diffuse Indirect','Diffuse Color','Glossy Direct','Glossy Indirect','Glossy Color','Emission'],'visibility':'Students hidden for clean architectural views; original collection retained','geometry':'No topology edits; copied mesh data for physically scaled UVs; subtle shader bevels','source_save':False,'overwrite_policy':'Only generated files in this isolated output directory'}
(R/'render_contract.json').write_text(json.dumps(contract,indent=2))
s.frame_set(1);report={'material_changes':[],'uv_objects':0,'lights':[],'source_sha256':source_hash}
for c in bpy.data.collections:
 if 'STUDENTS' in c.name.upper():c.hide_render=True;c.hide_viewport=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
assert any(d.use and '4090' in d.name for d in prefs.devices)
s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=256;s.cycles.adaptive_threshold=.01;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_min_samples=32
s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.use_light_tree=True
s.cycles.max_bounces=12;s.cycles.diffuse_bounces=4;s.cycles.glossy_bounces=4;s.cycles.transmission_bounces=12;s.cycles.transparent_max_bounces=16
s.cycles.caustics_reflective=False;s.cycles.caustics_refractive=False;s.cycles.sample_clamp_indirect=5;s.cycles.blur_glossy=.5
s.render.use_persistent_data=True;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False
s.render.pixel_aspect_x=1;s.render.pixel_aspect_y=1;s.render.film_transparent=False;s.render.use_file_extension=True
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.2
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='16';s.render.image_settings.compression=25
s.render.use_compositing=False
vl=s.view_layers[0];vl.cycles.denoising_store_passes=True
for p in ['use_pass_z','use_pass_normal','use_pass_diffuse_direct','use_pass_diffuse_indirect','use_pass_diffuse_color','use_pass_glossy_direct','use_pass_glossy_indirect','use_pass_glossy_color','use_pass_emit']:setattr(vl,p,True)
scales={'Natural oak':(.8,.8),'Acoustic panel neutral':(.8,.8),'Gray thin brick':(1,1.2),'Warm ivory facade brick':(1,1.2),'Light stone paving':(1.2,1.2),'V8 plain sage upholstery':(1,1),'Warm white plaster':(1.5,1.5)}
def image(path,noncolor=False):
 im=bpy.data.images.load(str(path),check_existing=True)
 if noncolor:im.colorspace_settings.name='Non-Color'
 im.pack();return im
def node(nt,typ):return nt.nodes.new(typ)
def pbr_material(name,asset,folder,size,roughrange,normstrength,tint=None):
 m=bpy.data.materials[name];m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
 bs=node(nt,'ShaderNodeBsdfPrincipled');out=node(nt,'ShaderNodeOutputMaterial');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
 uv=node(nt,'ShaderNodeUVMap');uv.uv_map='Cycles_PBR'
 tex={}
 for kind in ['Color','NormalDX','Roughness']:
  t=node(nt,'ShaderNodeTexImage');t.image=image(folder/(asset+'_'+size+'-JPG_'+kind+'.jpg'),kind!='Color');nt.links.new(uv.outputs['UV'],t.inputs['Vector']);tex[kind]=t
 if tint:
  ramp=node(nt,'ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=tuple(c*.8 for c in tint)+(1,);ramp.color_ramp.elements[1].color=tuple(min(1,c*1.12) for c in tint)+(1,)
  nt.links.new(tex['Color'].outputs['Color'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
 else:nt.links.new(tex['Color'].outputs['Color'],bs.inputs['Base Color'])
 rough=node(nt,'ShaderNodeMapRange');rough.inputs['To Min'].default_value=roughrange[0];rough.inputs['To Max'].default_value=roughrange[1];nt.links.new(tex['Roughness'].outputs['Color'],rough.inputs['Value']);nt.links.new(rough.outputs['Result'],bs.inputs['Roughness'])
 # DirectX normal maps use the opposite green convention to Blender.
 sep=node(nt,'ShaderNodeSeparateColor');comb=node(nt,'ShaderNodeCombineColor');flip=node(nt,'ShaderNodeMath');flip.operation='SUBTRACT';flip.inputs[0].default_value=1
 nt.links.new(tex['NormalDX'].outputs['Color'],sep.inputs[0]);nt.links.new(sep.outputs['Red'],comb.inputs['Red']);nt.links.new(sep.outputs['Green'],flip.inputs[1]);nt.links.new(flip.outputs[0],comb.inputs['Green']);nt.links.new(sep.outputs['Blue'],comb.inputs['Blue'])
 normal=node(nt,'ShaderNodeNormalMap');normal.uv_map='Cycles_PBR';normal.inputs['Strength'].default_value=normstrength;nt.links.new(comb.outputs[0],normal.inputs['Color']);nt.links.new(normal.outputs[0],bs.inputs['Normal'])
 report['material_changes'].append(name)
wood=R/'assets/Wood049'
pbr_material('Natural oak','Wood049',wood,'2K',(.32,.55),.2)
pbr_material('Acoustic panel neutral','Wood049',wood,'2K',(.55,.78),.12)
pbr_material('V8 plain sage upholstery','Fabric030',R/'assets/Fabric030','1K',(.75,.92),.22,(.24,.31,.27))
pbr_material('Warm white plaster','PaintedPlaster017',R/'assets/PaintedPlaster017','1K',(.72,.88),.1,(.76,.74,.69))
for name in ['Gray thin brick','Warm ivory facade brick','Light stone paving']:
 m=bpy.data.materials[name];nt=m.node_tree;uv=node(nt,'ShaderNodeUVMap');uv.uv_map='Cycles_PBR'
 for n in list(nt.nodes):
  if n.type=='TEX_IMAGE':nt.links.new(uv.outputs['UV'],n.inputs['Vector'])
  if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.1;n.uv_map='Cycles_PBR'
 report['material_changes'].append(name)
for ob in s.objects:
 if ob.type!='MESH' or not any(m and m.name in scales for m in ob.data.materials):continue
 ob.data=ob.data.copy();me=ob.data;uv=me.uv_layers.get('Cycles_PBR') or me.uv_layers.new(name='Cycles_PBR');me.uv_layers.active=uv;uv.active_render=True
 normalmatrix=ob.matrix_world.to_3x3().inverted_safe().transposed()
 for face in me.polygons:
  mat=me.materials[face.material_index] if face.material_index<len(me.materials) else None
  if not mat or mat.name not in scales:continue
  scale=scales[mat.name];normal=normalmatrix@face.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=(0,1) if axis==2 else (0,2) if axis==1 else (1,2)
  for li in face.loop_indices:
   p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/scale[0],p[axes[1]]/scale[1])
 report['uv_objects']+=1
for name,rough,metal in [('Anodized aluminum',.28,.85),('Brushed stainless hardware',.24,1),('Dark metal',.34,.85),('V8 plain porcelain',.18,0),('V8 plain light table surface',.38,0)]:
 m=bpy.data.materials.get(name)
 if not m or not m.use_nodes:continue
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 bevel=node(m.node_tree,'ShaderNodeBevel');bevel.samples=3;bevel.inputs['Radius'].default_value=.002;m.node_tree.links.new(bevel.outputs['Normal'],bs.inputs['Normal'])
glass=bpy.data.materials['Clear architectural glazing'];nt=glass.node_tree;nt.nodes.clear();bs=node(nt,'ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(.96,.985,1,1);bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45;bs.inputs['Roughness'].default_value=.025
lp=node(nt,'ShaderNodeLightPath');transparent=node(nt,'ShaderNodeBsdfTransparent');mix=node(nt,'ShaderNodeMixShader');out=node(nt,'ShaderNodeOutputMaterial');nt.links.new(lp.outputs['Is Shadow Ray'],mix.inputs[0]);nt.links.new(bs.outputs[0],mix.inputs[1]);nt.links.new(transparent.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
report['glass']='Refractive visible glass with transparent shadow-ray approximation for efficient daylight'
world=bpy.data.worlds.new('Cycles_Architectural_Daylight');world.use_nodes=True;s.world=world;nt=world.node_tree;nt.nodes.clear();sky=node(nt,'ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_disc=False;sky.sun_elevation=math.radians(35);sky.sun_rotation=math.radians(115);sky.air_density=1;sky.aerosol_density=2;sky.ozone_density=1.3
bg=node(nt,'ShaderNodeBackground');bg.inputs['Strength'].default_value=.3;out=node(nt,'ShaderNodeOutputWorld');nt.links.new(sky.outputs[0],bg.inputs['Color']);nt.links.new(bg.outputs[0],out.inputs['Surface'])
for o in s.objects:
 if o.type!='LIGHT':continue
 if o.name in ['Key','Fill']:o.hide_render=True;continue
 if o.data.type=='SUN':o.data.energy=2.2;o.data.angle=math.radians(1);o.rotation_euler=(math.radians(55),0,math.radians(-35));o.data.color=(1,.91,.78)
 else:o.data.color=(1,.86,.70)
 report['lights'].append({'name':o.name,'energy':o.data.energy,'color':list(o.data.color)})
shots=[('01_Entrance',(22,12.07,1.65),(7,12.07,1.65),24),('02_Commons',(9,14.5,1.65),(4.1,28.6,2.5),24),('03_iLab',(-2,9.2,1.7),(-7,4.5,1.2),24)]
coll=bpy.data.collections.new('CYCLES - architectural still cameras');s.collection.children.link(coll)
for name,p,t,lens in shots:
 data=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,data);coll.objects.link(cam);cam.location=p;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.sensor_width=36;data.clip_start=.05;data.clip_end=500
 data.dof.use_dof=True;data.dof.aperture_fstop=8;data.dof.focus_distance=(Vector(t)-cam.location).length
s.camera=bpy.data.objects['02_Commons'];s['cycles_studio_version']='v01';s['original_walkthrough_camera']='Walkthrough_Camera';s['students_hidden_for_stills']=True
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Cycles_Studio.blend'))
report['devices']=[{'name':d.name,'type':d.type,'enabled':d.use} for d in prefs.devices];report['cameras']=[a[0] for a in shots];report['objects']=len(s.objects)
(R/'build_report.json').write_text(json.dumps(report,indent=2));assert hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest()==source_hash
print('STUDIO_BUILD_COMPLETE',flush=True)




