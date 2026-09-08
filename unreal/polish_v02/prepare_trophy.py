import bpy,json,pathlib
from mathutils import Vector,Matrix
root=pathlib.Path(__file__).parent
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
report={'objects':[{'name':o.name,'polygons':len(o.data.polygons),'modifiers':[m.type for m in o.modifiers]} for o in meshes]}
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
before=sum(len(p.vertices)-2 for p in o.data.polygons)
if before>8000:
 mod=o.modifiers.new('Realtime_budget','DECIMATE');mod.ratio=8000/before;bpy.ops.object.modifier_apply(modifier=mod.name)
pts=[o.matrix_world@v.co for v in o.data.vertices];lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
factor=.30/(hi.z-lo.z)
for v in o.data.vertices:v.co=(o.matrix_world@v.co-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)))*factor
o.matrix_world=Matrix.Identity(4);o.name='Trophy_CC0_JeremyWoods'
bpy.context.scene.unit_settings.scale_length=1.0;bpy.context.view_layer.update()
m=bpy.data.materials.new('Trophy_satin_brass');m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.63,.39,.10,1);n.inputs['Metallic'].default_value=1;n.inputs['Roughness'].default_value=.27
o.data.materials.clear();o.data.materials.append(m)
for p in o.data.polygons:p.use_smooth=True
report.update({'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'height_m':.30,'dimensions_m':list(o.dimensions),'source':'https://opengameart.org/content/trophy','license':'CC0','author':'JeremyWoods','status':'prepared candidate; not placed in building'})
bpy.ops.export_scene.gltf(filepath=str(root/'Trophy_Optimized.glb'),export_format='GLB',use_selection=True)
(root/'trophy_report.json').write_text(json.dumps(report,indent=2))
scene=bpy.context.scene
for other in list(scene.objects):
 if other!=o:bpy.data.objects.remove(other,do_unlink=True)
camdata=bpy.data.cameras.new('AssetReview');cam=bpy.data.objects.new('AssetReview',camdata);scene.collection.objects.link(cam);cam.location=(.6,-.8,.5);cam.rotation_euler=(Vector((0,0,.15))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.8;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';o.color=(.63,.39,.10,1);scene.render.resolution_x=512;scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.filepath=str(root/'Trophy_Review.png');bpy.ops.render.render(write_still=True)
