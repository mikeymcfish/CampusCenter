from pathlib import Path
import bpy,math
from mathutils import Vector
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Campus_Center_Furnished_Print.blend'))
s=bpy.context.scene;o=next(x for x in s.objects if x.type=='MESH');c=s.camera
# Close inspection view of real integrated seating and laboratory furniture.
c.location=(.93,-.11,.46);target=Vector((.63,.13,.012));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=.36
s.render.resolution_x=1500;s.render.resolution_y=1125;s.cycles.samples=48
s.render.filepath=str(R/'Furnished_Detail_Preview.png');bpy.ops.render.render(write_still=True)
# A digital preview of overhead illumination on the exact printable surface.
uv=o.data.uv_layers.new(name='Fixed overhead projector XY')
width=.790426;height=width*1572/2048
for p in o.data.polygons:
    for li in p.loop_indices:
        v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
        uv.data[li].uv=((v.x-.3845)/width+.5,(v.y-.289)/height+.5)
m=bpy.data.materials.new('Informational projection - replace image for another chapter');m.use_nodes=True;n=m.node_tree.nodes;n.clear();links=m.node_tree.links
out=n.new('ShaderNodeOutputMaterial');add=n.new('ShaderNodeAddShader');diff=n.new('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(.12,.12,.12,1);diff.inputs['Roughness'].default_value=.9
e=n.new('ShaderNodeEmission');e.inputs['Strength'].default_value=.9;tex=n.new('ShaderNodeTexImage');tex.interpolation='Closest';tex.extension='CLIP'
geom=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');clamp=n.new('ShaderNodeMath');clamp.operation='MAXIMUM';clamp.inputs[1].default_value=0
links.new(geom.outputs['Normal'],sep.inputs[0]);links.new(sep.outputs['Z'],clamp.inputs[0]);links.new(clamp.outputs[0],e.inputs['Strength'])
coord=n.new('ShaderNodeUVMap');coord.uv_map=uv.name;links.new(coord.outputs['UV'],tex.inputs['Vector']);links.new(tex.outputs['Color'],e.inputs['Color']);links.new(e.outputs[0],add.inputs[0]);links.new(diff.outputs[0],add.inputs[1]);links.new(add.outputs[0],out.inputs['Surface'])
o.data.materials.clear();o.data.materials.append(m)
for p in o.data.polygons:p.material_index=0
for light in (x for x in s.objects if x.type=='LIGHT'):light.data.energy=2 if light.name=='Key' else .8
s.world.node_tree.nodes.get('Background').inputs[1].default_value=.1;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.cycles.samples=64;s.cycles.max_bounces=2
c.location=(.81,-.43,1.18);target=Vector((.385,.289,.015));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=.9
s.render.resolution_x=1600;s.render.resolution_y=1230
for chapter in [1,3]:
    tex.image=bpy.data.images.load(str(R/'information'/f'Chapter_{chapter:02d}.png'),check_existing=True);tex.image.pack()
    s.render.filepath=str(R/f'Information_On_Model_{chapter:02d}.png');bpy.ops.render.render(write_still=True)
s['preview_status']='Digital overhead projection preview; physical projector calibration has not been performed.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Information_Preview.blend'))
print('PRESENTATION_PREVIEWS_COMPLETE',flush=True)
