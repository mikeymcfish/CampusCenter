import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).parent;out=r/'plaque_cleaned';d=json.loads((out/'outline.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(r/'cleaned/SilverCup.blend'))
for o in list(bpy.data.objects):
 if o.type=='MESH' and not o.name.lower().startswith(('floor','ground')):bpy.data.objects.remove(o,do_unlink=True)
parts=[]
wood=bpy.data.materials.get('Cup_Plinth_Step_Wood') or next(m for m in bpy.data.materials if 'Walnut' in m.name)
# Reuse the cup's embedded baked walnut map, with new UVs.
silver=next(m for m in bpy.data.materials if m.name=='Clean_Polished_Silver').copy();silver.name='Plaque_Satin_Silver';silver.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.32
def finish(o,mat,bevel):
 o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;o.select_set(True)
 if bevel:
  mod=o.modifiers.new('Soft_edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent if False else None
 bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False);parts.append(o)
def extrude(name,poly,y0,y1,mat,bevel):
 n=len(poly);verts=[(x,y,z) for y in (y0,y1) for x,z in poly]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();finish(o,mat,bevel);return o
def box(name,loc,dims,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,mat,.0008)
outer=d['outer'];outer=[(x,max(.038,z)) for x,z in outer]
extrude('Trellis_Derived_Wood_Silhouette',outer,-.004,.004,wood,.00035)
extrude('Blank_Satin_Inset',d['inner'],-.0049,-.0041,silver,.00015)
box('Plaque_Plinth_Lower',(0,0,.013),(.2286,.1076,.026),wood)
box('Plaque_Plinth_Upper',(0,0,.032),(.202,.080,.012),wood)
box('Blank_Base_Plate',(0,-.054,.014),(.160,.001,.014),silver)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True
for ob in parts:
 if ob.data.materials[0]!=wood:continue
 mat=wood.copy();ob.data.materials[0]=mat;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');output=next(x for x in n if x.type=='OUTPUT_MATERIAL')
 for x in list(n):
  if x not in [bs,output]:n.remove(x)
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7
 coord=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1,20,4);l.new(coord.outputs['Generated'],scale.inputs[0]);l.new(scale.outputs[0],noise.inputs[0])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.035,.014,.006,1);ramp.color_ramp.elements[1].color=(.14,.065,.027,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
 emit=n.new('ShaderNodeEmission');l.new(ramp.outputs[0],emit.inputs['Color']);l.new(emit.outputs[0],output.inputs[0])
 img=bpy.data.images.new(ob.name+'_Walnut',width=512,height=512);tex=n.new('ShaderNodeTexImage');tex.image=img;n.active=tex
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;scene.render.bake.margin=8;bpy.ops.object.bake(type='EMIT');img.filepath_raw=str(out/(ob.name+'_Walnut.png'));img.file_format='PNG';img.save();img.pack()
 l.new(tex.outputs[0],bs.inputs['Base Color']);l.new(bs.outputs[0],output.inputs[0])
 for x in list(n):
  if x not in [bs,output,tex]:n.remove(x)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'RegionalPlaque.glb'),use_selection=True,export_format='GLB')
bpy.ops.export_scene.fbx(filepath=str(out/'RegionalPlaque.fbx'),use_selection=True,axis_forward='-Z',axis_up='Y',path_mode='COPY',embed_textures=True)
stats=[]
for o in parts:
 bm=bmesh.new();bm.from_mesh(o.data);stats.append({'name':o.name,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'uv_layers':len(o.data.uv_layers)});bm.free()
for view,a,z in [('front',0,.20),('side',math.pi/2,.20),('rear',math.pi,.20),('oblique',math.pi/4,.24)]:
 c=scene.camera;c.location=(math.sin(a),-math.cos(a),z);c.rotation_euler=(Vector((0,0,.15))-c.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/('RegionalPlaque_'+view+'.png'));bpy.ops.render.render(write_still=True)
scene['provenance']='Trellis-derived silhouette manually extruded and rebuilt; blank generic prototype, no authentic award inscription'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'RegionalPlaque.blend'))
(out/'manifest.json').write_text(json.dumps({'provenance':scene['provenance'],'dimensions_m':[.2286,.1086,.30],'parts':stats,'total_triangles':sum(x['triangles'] for x in stats),'lod_note':'Already compact; same mesh suitable for lower LOD until screen-size integration testing','raw_archive':'../prototypes/plaque_raw_trellis.glb','source_sha256':'a9430736a64104ff90c43b4473de6a6ce1dd8c677dc591770a6e2e04bf344c4e','model_revision':'af44b45f2e35a493886929c6d786e563ec68364d','outline':d['provenance'],'limits':['Separate closed render components overlap at support contact; not a fabrication union','Region contour inferred from one supplied reference; generic blank prototype']},indent=2))
print('PLAQUE BUILT',stats)
