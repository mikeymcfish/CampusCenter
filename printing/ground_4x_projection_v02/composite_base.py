import bpy,pathlib,json
R=pathlib.Path(__file__).parent
# A separate deterministic Blender compositing scene. No edits to generated image pixels.
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False
s.render.resolution_x=1024;s.render.resolution_y=786;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.film_transparent=False
s.render.dither_intensity=0;s.cycles.filter_width=.01
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0
s.world=bpy.data.worlds.new('Black');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[1].default_value=0
cd=bpy.data.cameras.new('Projection pixel camera');c=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(c);c.location=(.5,.5,2);cd.type='ORTHO';cd.ortho_scale=1;cd.sensor_fit='HORIZONTAL';s.camera=c
aspect=786/1024;bpy.ops.mesh.primitive_plane_add(size=1,location=(.5,.5,0));plane=bpy.context.object;plane.scale=(1,aspect,1)
m=bpy.data.materials.new('Hard projector floor mask');m.use_nodes=True;plane.data.materials.append(m);n=m.node_tree.nodes;n.clear();links=m.node_tree.links
uv=n.new('ShaderNodeTexCoord');mask=bpy.data.images.load(str(R/'floor_mask_raw.png'));mask.colorspace_settings.name='Non-Color'
last=None
for dx,dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
 add=n.new('ShaderNodeVectorMath');add.operation='ADD';links.new(uv.outputs['UV'],add.inputs[0]);add.inputs[1].default_value=(dx/1024,dy/786,0)
 tex=n.new('ShaderNodeTexImage');tex.image=mask;tex.interpolation='Closest';tex.extension='CLIP';links.new(add.outputs[0],tex.inputs[0])
 threshold=n.new('ShaderNodeMath');threshold.operation='GREATER_THAN';threshold.inputs[1].default_value=.98;links.new(tex.outputs[0],threshold.inputs[0])
 if last:
  mn=n.new('ShaderNodeMath');mn.operation='MINIMUM';links.new(last,mn.inputs[0]);links.new(threshold.outputs[0],mn.inputs[1]);last=mn.outputs[0]
 else:last=threshold.outputs[0]
em=n.new('ShaderNodeEmission');em.inputs[1].default_value=1;out=n.new('ShaderNodeOutputMaterial');links.new(em.outputs[0],out.inputs[0]);links.new(last,em.inputs[0]);s.render.filepath=str(R/'floor_only_mask.png');bpy.ops.render.render(write_still=True)
base=n.new('ShaderNodeTexImage');base.image=bpy.data.images.load(str(R/'base_beauty_unmasked.png'));base.interpolation='Closest';links.new(uv.outputs['UV'],base.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;links.new(base.outputs[0],mix.inputs[1]);links.new(last,mix.inputs[2]);links.new(mix.outputs[0],em.inputs[0]);s.render.filepath=str(R/'Projection_Base_Top_Down.png');bpy.ops.render.render(write_still=True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Projection_Output_Compositor.blend'))
