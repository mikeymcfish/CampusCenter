import bpy,pathlib,json
from mathutils import Vector
R=pathlib.Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(R/'print/Campus_Center_Projection_Receiver.blend'));s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
s.cycles.device='GPU';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.filter_width=1.0;s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=False;o.data.energy*=.018
s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.02,.03,.045,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.05
black=bpy.data.materials.get('Projection blackout');black.node_tree.nodes.clear();p=black.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.5,.52,.54,1);p.inputs['Roughness'].default_value=.9;out=black.node_tree.nodes.new('ShaderNodeOutputMaterial');black.node_tree.links.new(p.outputs['BSDF'],out.inputs[0])
on=bpy.data.materials.get('Projection receiver');nt=on.node_tree;n=nt.nodes;n.clear();geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);comb=n.new('ShaderNodeCombineXYZ')
for axis,span,center in [('X',.830,.398),('Y',.63708984375,.289)]:
 mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=1/span;mul.inputs[2].default_value=.5-center/span;nt.links.new(sep.outputs[axis],mul.inputs[0]);nt.links.new(mul.outputs[0],comb.inputs[axis])
tex=n.new('ShaderNodeTexImage');tex.interpolation='Linear';tex.extension='CLIP';nt.links.new(comb.outputs[0],tex.inputs['Vector']);em=n.new('ShaderNodeEmission');em.inputs[1].default_value=1.8;nt.links.new(tex.outputs['Color'],em.inputs[0]);out=n.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
c=s.camera;c.location=(.93,-.52,.87);c.rotation_euler=(Vector((.398,.289,.013))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=.99
outdir=R/'projection/review';outdir.mkdir(exist_ok=True)
for name,path in [('Ink_Map','assets/Ink_Map.png'),('Depth_Contours','examples/Depth_Contours_Preview.png'),('Surface_Ripples','examples/Surface_Ripples_Preview.png'),('Explorer','examples/Explorer_Preview.png')]:
 tex.image=bpy.data.images.load(str(R/'projection'/path),check_existing=True);s.render.filepath=str(outdir/(name+'_On_Print.png'));bpy.ops.render.render(write_still=True);print('PROJECTION_VIEW',name,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Projection_Review.blend'))
