import unreal,pathlib,json
ed=unreal.MaterialEditingLibrary;root=pathlib.Path(unreal.Paths.project_dir());report=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/PolishV03/Materials',recursive=True):
 m=unreal.load_asset(path)
 if not isinstance(m,unreal.Material):continue
 name=m.get_name()
 scale=(80,80) if 'Oak' in name else (120,120) if 'stone' in name else (100,120) if 'brick' in name else None
 if not scale:continue
 def node(c):return ed.create_material_expression(m,c)
 def wire(a,o,b,i):
  names=list(ed.get_material_expression_input_names(b))
  if i in ['AGreaterThanB','AEqualsB','ALessThanB']:i=names[{'AGreaterThanB':2,'AEqualsB':3,'ALessThanB':4}[i]]
  if i=='Input' and len(names)==1:i=names[0]
  assert ed.connect_material_expressions(a,o,b,i),(b.get_class().get_name(),i,names)
 def scalar(v):n=node(unreal.MaterialExpressionConstant);n.r=v;return n
 def mask(src,r,g,b):
  n=node(unreal.MaterialExpressionComponentMask);n.set_editor_property('r',r);n.set_editor_property('g',g);n.set_editor_property('b',b);n.set_editor_property('a',False);wire(src,'',n,'Input');return n
 world=node(unreal.MaterialExpressionWorldPosition);normal=node(unreal.MaterialExpressionVertexNormalWS);absn=node(unreal.MaterialExpressionAbs);wire(normal,'',absn,'Input')
 xy=mask(world,True,True,False);xz=mask(world,True,False,True);yz=mask(world,False,True,True)
 def choose(test,yes,no):
  n=node(unreal.MaterialExpressionIf);wire(test,'',n,'A');wire(scalar(.5),'',n,'B');wire(yes,'',n,'AGreaterThanB');wire(yes,'',n,'AEqualsB');wire(no,'',n,'ALessThanB');return n
 side=choose(mask(absn,True,False,False),yz,xz);projected=choose(mask(absn,False,False,True),xy,side)
 divisor=node(unreal.MaterialExpressionConstant2Vector);divisor.r=scale[0];divisor.g=scale[1]
 uv=node(unreal.MaterialExpressionDivide);wire(projected,'',uv,'A');wire(divisor,'',uv,'B')
 # Existing texture sample nodes: query all expressions through the editor asset property.
 expressions=[]
 def visit(n):
  if not n or n in expressions:return
  expressions.append(n)
  for child in ed.get_inputs_for_material_expression(m,n):visit(child)
 for prop in [unreal.MaterialProperty.MP_BASE_COLOR,unreal.MaterialProperty.MP_NORMAL,unreal.MaterialProperty.MP_ROUGHNESS]:visit(ed.get_material_property_input_node(m,prop))
 for n in expressions:
  if isinstance(n,unreal.MaterialExpressionTextureSample):wire(uv,'',n,'UVs')
 ed.recompile_material(m);ed.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_NANITE);unreal.EditorAssetLibrary.save_loaded_asset(m);report.append({'material':name,'world_tile_cm':scale})
(root/'world_mapping_v03.json').write_text(json.dumps(report,indent=2))



