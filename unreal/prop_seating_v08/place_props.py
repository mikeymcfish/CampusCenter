import math
actors=list(A.get_all_level_actors())
bylabel={a.get_actor_label():a for a in actors}
report={'laptops':[],'cups':[],'trophies':[],'seating':[]}
def vec(v):return [v.x,v.y,v.z]
def bounds(group):
 pairs=[a.get_actor_bounds(False) for a in group]
 lo=[min(vec(o)[i]-vec(e)[i] for o,e in pairs) for i in range(3)]
 hi=[max(vec(o)[i]+vec(e)[i] for o,e in pairs) for i in range(3)]
 return lo,hi
def prop(kind,index,support,dx,dy,yaw):
 table=bylabel[support];o,e=table.get_actor_bounds(False);top=o.z+e.z
 if kind=='laptops':
  src=[a for a in actors if a.get_actor_label()=='StaticMeshActor0' and any(c.static_mesh and '/macbook_laptop/' in c.static_mesh.get_path_name() for c in a.get_components_by_class(unreal.StaticMeshComponent))]
 else:src=[bylabel['coffeecup']]
 group=[]
 for j,a in enumerate(src):
  c=a.get_component_by_class(unreal.StaticMeshComponent)
  n=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator(yaw=yaw))
  n.set_actor_label('PS08_'+kind+'_%02d_part%d'%(index,j));n.set_folder_path('V08 additions/Tabletop props')
  nc=n.static_mesh_component;nc.set_static_mesh(c.static_mesh)
  for k,m in enumerate(c.get_materials()):nc.set_material(k,m)
  n.set_actor_scale3d(a.get_actor_scale3d());nc.set_collision_profile_name('NoCollision');group.append(n)
 assert len(group)==(3 if kind=='laptops' else 1)
 lo,hi=bounds(group);shift=unreal.Vector(o.x+dx-(lo[0]+hi[0])/2,o.y+dy-(lo[1]+hi[1])/2,top+.10-lo[2])
 for n in group:n.set_actor_location(n.get_actor_location()+shift,False,False)
 lo,hi=bounds(group)
 assert lo[0]>=o.x-e.x+2 and hi[0]<=o.x+e.x-2 and lo[1]>=o.y-e.y+2 and hi[1]<=o.y+e.y-2,(support,lo,hi)
 report[kind].append({'support':support,'actors':[n.get_actor_label() for n in group],'bounds':[lo,hi],'tabletop_z':top,'gap_cm':lo[2]-top})
prefix='StandardV07_V8_DETAIL_V6_'
for i,(name,x,y,yaw) in enumerate([('104_desk',-39,-3,90),('111_desk',-39,-3,90),('112_group_table',-16,55,0),('113_group_table',16,-50,180),('209_student_table_20',0,0,90),('202_visitor_table',0,0,90)],1):
 prop('laptops',i,prefix+name,x,y,yaw)
for i,(name,x,y,yaw) in enumerate([('104_desk',43,-15,10),('111_desk',42,-14,-20),('112_group_table',-10,92,30),('113_group_table',16,-87,-15),('209_student_table_20',35,-8,60),('202_visitor_table',31,12,25)],1):
 prop('cups',i,prefix+name,x,y,yaw)
(R/'props_report.json').write_text(json.dumps(report,indent=2))
