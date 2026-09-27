E=unreal.EditorAssetLibrary;M=unreal.MaterialEditingLibrary
D='/Game/Campus/PropSeatingV08'
def material(name,color,metal,rough):
 path=D+'/'+name
 m=unreal.load_asset(path) if E.does_asset_exist(path) else unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,D,unreal.Material,unreal.MaterialFactoryNew())
 M.delete_all_material_expressions(m)
 c=M.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.constant=unreal.LinearColor(*color,1);M.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for prop,value in [(unreal.MaterialProperty.MP_METALLIC,metal),(unreal.MaterialProperty.MP_ROUGHNESS,rough)]:
  n=M.create_material_expression(m,unreal.MaterialExpressionConstant);n.r=value;M.connect_material_property(n,'',prop)
 M.recompile_material(m);E.save_loaded_asset(m);return m
navy=material('M_Bleacher_Navy',(.018,.055,.12),.12,.36)
metal=material('M_Bleacher_Aluminum',(.44,.49,.54),.82,.34)
dark=material('M_Bleacher_Frame',(.055,.066,.08),.65,.42)
edge=material('M_Bleacher_StepEdge',(.72,.57,.20),.1,.55)
cube=unreal.load_asset('/Engine/BasicShapes/Cube.Cube');cyl=unreal.load_asset('/Engine/BasicShapes/Cylinder.Cylinder')
def piece(name,p,size,mat,round=False,rot=None):
 a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*p),rot or unreal.Rotator())
 a.set_actor_label('PS08_Bleacher_'+name);a.set_folder_path('V08 additions/Gym bleachers')
 c=a.static_mesh_component;c.set_static_mesh(cyl if round else cube);c.set_material(0,mat);c.set_collision_profile_name('BlockAll');a.set_actor_scale3d(unreal.Vector(*[v/100 for v in size]));report['seating'].append(a.get_actor_label());return a
for bank,yc in enumerate([-2700,-3480],1):
 for row in range(3):
  x=-302.5+75*row;z=30*row
  piece(f'{bank}_deck_{row}',(x,yc,z+2),(75,600,4),metal)
  piece(f'{bank}_riser_{row}',(x-37,yc,max(1,z/2)),(2,600,max(2,z)),dark)
  for seg in range(12):
   yy=yc-275+50*seg
   piece(f'{bank}_seat_{row}_{seg}',(x+14,yy,z+45),(34,49,5),navy)
  for yy in [yc-280,yc-140,yc,yc+140,yc+280]:
   piece(f'{bank}_seatleg_{row}_{yy}',(x+14,yy,z+24),(5,5,40),dark)
   if row:piece(f'{bank}_underframe_{row}_{yy}',(x,yy,z/2),(5,5,z),dark)
  piece(f'{bank}_beam_{row}',(x+14,yc,z+37),(5,592,5),metal)
 # Guarding follows the back and the two exposed ends; front stays open.
 for yy in [yc-299,yc-150,yc,yc+150,yc+299]:
  piece(f'{bank}_backpost_{yy}',(-115,yy,115),(4,4,110),metal,True)
 for z in [115,170]:piece(f'{bank}_backrail_{z}',(-115,yc,z),(4,4,600),metal,True,unreal.Rotator(roll=90))
 for yy in [yc+299 if bank==1 else yc-299]:
  for row in range(3):
   x=-302.5+75*row;z=30*row
   piece(f'{bank}_sidepost_{yy}_{row}',(x,yy,z+55),(4,4,110),metal,True)
   piece(f'{bank}_sideguard_{yy}_{row}',(x,yy,z+88),(70,3,3),metal)
   piece(f'{bank}_sidehandrail_{yy}_{row}',(x,yy,z+110),(74,4,4),metal)
 # Fine longitudinal grooves on aluminum walking decks.
 for row in range(3):
  for off in [-28,-20,-12]:piece(f'{bank}_deckgroove_{row}_{off}',(-302.5+75*row+off,yc,30*row+4.05),(.45,595,.1),dark)
for i in range(4):
 x=-283.75+i*37.5;h=15*(i+1)
 piece(f'aisle_step_{i}',(x,-3090,h/2),(37.5,170,h),metal)
 piece(f'aisle_nosing_{i}',(x-16.75,-3090,h+.12),(4,170,.24),edge)
(R/'bleachers_report.json').write_text(json.dumps({'actors':report['seating'],'banks':2,'rows_per_bank':3,'seating_positions':72,'central_aisle_cm':180,'footprint_cm':{'x':[-340,-113],'y':[-3780,-2400]}},indent=2))
