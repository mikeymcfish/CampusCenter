import bpy, pathlib, json, hashlib, re
R=pathlib.Path(__file__).parent
s=bpy.context.scene
sha=hashlib.sha256((R/'Source_Copy.blend').read_bytes()).hexdigest()
def rgb(hex):
 v=[int(hex[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in v)+(1,)
paint=bpy.data.materials['Warm white plaster'].copy();paint.name='V02 Light blue matte interior paint'
nt=paint.node_tree
for n in nt.nodes:
 if n.type=='VALTORGB':
  n.color_ramp.elements[0].color=rgb('ACC6D8');n.color_ramp.elements[1].color=rgb('BDD4E3')
 if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=.85;n.inputs['To Max'].default_value=.95
 if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.065
paint.diffuse_color=rgb('B6CDDF')
def region(nt,bounds):
 g=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],sep.inputs[0]);terms=[]
 for axis,lo,hi in bounds:
  for op,value in [('GREATER_THAN',lo),('LESS_THAN',hi)]:
   n=nt.nodes.new('ShaderNodeMath');n.operation=op;n.inputs[1].default_value=value;nt.links.new(sep.outputs[axis],n.inputs[0]);terms.append(n.outputs[0])
 out=terms[0]
 for term in terms[1:]:
  n=nt.nodes.new('ShaderNodeMath');n.operation='MULTIPLY';nt.links.new(out,n.inputs[0]);nt.links.new(term,n.inputs[1]);out=n.outputs[0]
 return out
def bounded_paint(base,bounds):
 m=base.copy();m.name='V02 Commons blue feature wall';nt=m.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');old=out.inputs['Surface'].links[0].from_socket
 bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=rgb('B6CDDF');bs.inputs['Roughness'].default_value=.9
 mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(region(nt,bounds),mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(bs.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface']);return m
commons=bounded_paint(bpy.data.materials['Gray thin brick'],[('Y',16.38,31.02)])
changes=[]
for o in s.objects:
 if o.type!='MESH':continue
 architectural=bool(re.search(r'_(wall\d*|lintel\d*|end|sill\d*|head\d*)$',o.name))
 if not architectural and o.name!='Gym_east':continue
 count=0;normalmat=o.matrix_world.to_3x3().inverted_safe().transposed()
 for f in o.data.polygons:
  if f.material_index>=len(o.data.materials):continue
  old=o.data.materials[f.material_index];n=(normalmat@f.normal).normalized()
  if abs(n.z)>.5:continue
  target=None
  if old.name=='Warm white plaster':
   target=paint
   # Glazed exterior envelope retains its original outer finish.
   if 'commons' in o.name.lower():
    if '_north_' in o.name and n.y>=-.5:target=None
    if '_east_' in o.name and n.x>=-.5:target=None
  elif old.name=='Warm ivory facade brick':
   for direction,axis,sign in [('north',1,-1),('south',1,1),('east',0,-1),('west',0,1)]:
    if '_'+direction+'_' in o.name and n[axis]*sign>.5:target=paint
  elif old.name=='Gray thin brick' and (o.name.startswith('Commons_gym_party_wall') or o.name=='Gym_east') and n.x>.5:target=commons
  if target:
   if target.name not in o.data.materials:o.data.materials.append(target)
   f.material_index=o.data.materials.find(target.name);count+=1
 if count:changes.append({'object':o.name,'painted_faces':count})
# A spatial finish on the existing slab keeps every furniture contact and mesh intact.
floor=bpy.data.objects['A101_ground_slab'];base=bpy.data.materials['Light stone paving'];m=base.copy();m.name='V02 Commons carpet and original stone';nt=m.node_tree
out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');old=out.inputs['Surface'].links[0].from_socket
g=nt.nodes.new('ShaderNodeNewGeometry');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=850;noise.inputs['Detail'].default_value=2;nt.links.new(g.outputs['Position'],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=rgb('526D82');ramp.color_ramp.elements[1].color=rgb('8196A5');nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.96;bs.inputs['Sheen Weight'].default_value=.25;nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
macro=nt.nodes.new('ShaderNodeTexNoise');macro.inputs['Scale'].default_value=55;macro.inputs['Detail'].default_value=2;nt.links.new(g.outputs['Position'],macro.inputs['Vector'])
variation=nt.nodes.new('ShaderNodeMixRGB');variation.blend_type='MULTIPLY';variation.inputs[0].default_value=.24;nt.links.new(ramp.outputs['Color'],variation.inputs[1]);nt.links.new(macro.outputs['Fac'],variation.inputs[2]);nt.links.new(variation.outputs[0],bs.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.3;bump.inputs['Distance'].default_value=.0006;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
bounds=[('X',.15,16.312),('Y',14.6283,30.887),('Z',-.001,.001)]
mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(region(nt,bounds),mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(bs.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
for i,mat in enumerate(floor.data.materials):
 if mat==base:floor.data.materials[i]=m
s['cycles_studio_version']='v02';s['finish_notes']='Light blue matte interior walls; blue-gray commons carpet; original exterior and fireplace brick accents retained.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Campus_Center_Cycles_Studio.blend'))
report={'source_sha256':sha,'paint_objects':changes,'paint_faces':sum(x['painted_faces'] for x in changes),'carpet_bounds_m':bounds,'mesh_count':sum(o.type=='MESH' for o in s.objects),'geometry_changed':False}
(R/'build_report.json').write_text(json.dumps(report,indent=2));print('COLOR_BUILD_COMPLETE',len(changes),report['paint_faces'],flush=True)
