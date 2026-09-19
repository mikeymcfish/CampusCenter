import bpy,pathlib,json,math,numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).parent/'print'
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
bpy.ops.wm.stl_import(filepath=str(R/'Campus_Center_Ground_Acrylic_1_87p5.stl'))
o=bpy.context.object;o.name='Enclosed ground floor - supported unified print';o.scale=(.001,.001,.001);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
def material(name,color,emission=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes
    if emission:
        n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],out.inputs[0])
    else:
        p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.82
    return m
white=material('Matte white print',(.77,.79,.8));o.data.materials.append(white)
s.render.engine='CYCLES';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices();[setattr(d,'use',d.type=='CUDA') for d in prefs.devices];s.cycles.device='GPU';s.cycles.samples=32;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.035
s.render.resolution_x=1600;s.render.resolution_y=1230;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.dither_intensity=0;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-1.3
world=bpy.data.worlds.new('Neutral print review studio');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.025,.035,.05,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.4;s.world=world
for name,loc,power,size in [('Key',(0,-.2,1),90,.75),('Fill',(.8,.7,.7),40,.6)]:
    d=bpy.data.lights.new(name,'AREA');l=bpy.data.objects.new(name,d);s.collection.objects.link(l);l.location=loc;l.rotation_euler=(Vector((.385,.289,0))-l.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.shape='DISK';d.size=size
d=bpy.data.cameras.new('Print inspection camera');c=bpy.data.objects.new(d.name,d);s.collection.objects.link(c);s.camera=c;d.type='ORTHO';d.ortho_scale=.95;d.clip_end=10
c.location=(.90,-.5,.88);target=Vector((.385,.289,.015));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(R/'Furnished_Print_Preview.png');bpy.ops.render.render(write_still=True)
# Default editable file opens in the clear inspection view.
s.unit_settings.system='METRIC';s['print_scale']='1:87.5';s['print_units']='STL and STEP in millimetres; Blender geometry in metres';s['projection_note']='Use exact receiving geometry; no painted furniture illusion on floor.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Furnished_Print.blend'))
c.location=(.398,.289,1);c.rotation_euler=(0,0,0);d.ortho_scale=.830;s.render.resolution_x=2048;s.render.resolution_y=1572
s.render.filepath=str(R/'Furnished_Print_Top.png');bpy.ops.render.render(write_still=True)
grid=np.load(R/'print_height_data.npz');g=grid['structural_reference'];h=grid['furniture'];pitch=float(grid['pitch_mm']);ny,nx=g.shape
black=material('Projection blackout',(0,0,0),True);on=material('Projection receiver',(1,1,1),True)
o.data.materials.clear();o.data.materials.append(black);o.data.materials.append(on)
floor_faces=[];furniture_faces=[]
for p in o.data.polygons:
    x,y,z=p.center*1000;ix=max(0,min(nx-1,int(x/pitch)));iy=max(0,min(ny-1,int(y/pitch)))
    if p.normal.z>.01 and abs(z-4.8)<.015:floor_faces.append(p.index)
    elif p.normal.z>.01 and g[iy,ix]<=4.801 and h[iy,ix]>4.801 and z>4.81:furniture_faces.append(p.index)
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.cycles.samples=1;s.cycles.use_denoising=False;s.cycles.filter_width=.01;world.node_tree.nodes.get('Background').inputs[1].default_value=0
for obj in s.objects:
    if obj.type=='LIGHT':obj.hide_render=True
for name,ids in [('floor_mask',floor_faces),('furniture_mask',furniture_faces),('receiver_mask',floor_faces+furniture_faces)]:
    ids=set(ids)
    for p in o.data.polygons:p.material_index=1 if p.index in ids else 0
    s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
s['projection_resolution']=[2048,1572];s['physical_canvas_mm']=[830.0,637.08984375]
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Projection_Receiver.blend'))
(R/'receiver_contract.json').write_text(json.dumps({'resolution':[2048,1572],'native_resolution':[1024,786],'center_mm':[398,289],'canvas_mm':[830.0,830.0*1572/2048],'projection':'Direct vertical orthographic','floor_faces':len(floor_faces),'furniture_faces':len(furniture_faces),'wall_tops_black':True,'upper_floor':False,'roof':False},indent=2))
print('PRINT_AND_MASKS_RENDERED',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'Campus_Center_Furnished_Print.blend'))
s=bpy.context.scene
bpy.ops.wm.stl_import(filepath=str(R/'Acrylic_Panes_Reference_ONLY.stl'))
pane=bpy.context.object;pane.name='Clear acrylic inserts - reference only';pane.scale=(.001,)*3
mat=bpy.data.materials.new('Clear acrylic demonstration');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.65,.90,.95,1);p.inputs['Roughness'].default_value=.12;p.inputs['Transmission Weight'].default_value=.85;p.inputs['IOR'].default_value=1.49;pane.data.materials.append(mat)
s.render.filepath=str(R/'Acrylic_Installed_Preview.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Acrylic_Assembly_Reference.blend'))

