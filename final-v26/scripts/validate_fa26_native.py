import unreal,pathlib,json,hashlib,math
R=pathlib.Path('C:/Users/mikef/Documents/Codex/2026-09-30/task/CampusCenter-new-plans');D=R/'downstream/furniture_art_v26_r01';P=pathlib.Path(unreal.Paths.project_dir()).resolve();f=json.loads((D/'enhancement-r15.json').read_text());stage=json.loads((D/'desktop-furniture-stage-r04.json').read_text());L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);assert L.load_level(f['map']);actors=A.get_all_level_actors();by={a.get_name():a for a in actors};world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();new=[a for a in actors if a.get_actor_label().startswith('FA26_')];art=[a for a in actors if a.get_actor_label().startswith('ART26_')];assert len(art)==11
def hit(h):
 if isinstance(h,(tuple,list)):h=next((x for x in h if isinstance(x,unreal.HitResult)),None)
 if not h:return None
 t=h.to_tuple();a=t[9];return {'blocking':bool(t[0]),'point_cm':t[5].to_tuple(),'label':a.get_actor_label() if a else None,'actor':a.get_name() if a else None}
materials=[]
for a in new+art:
 c=a.static_mesh_component;assert c.static_mesh
 for i in range(c.get_num_materials()):
  m=c.get_material(i);assert m;flag=bool(m.get_base_material().get_editor_property('used_with_nanite'));assert flag,(a.get_actor_label(),m.get_path_name());assert 'WorldGridMaterial' not in m.get_path_name();materials.append({'actor':a.get_actor_label(),'slot':i,'material':m.get_path_name(),'nanite_usage':flag})
support=[];clearance=[]
for row in stage['placements']:
 lo,hi=row['bounds_cm'];floor=426.72 if lo[2]>400 else 0;cx=(lo[0]+hi[0])/2;cy=(lo[1]+hi[1])/2;traces=[]
 for x,y in [(cx,cy),(lo[0]+5,lo[1]+5),(hi[0]-5,lo[1]+5),(lo[0]+5,hi[1]-5),(hi[0]-5,hi[1]-5)]:
  traces.append(hit(unreal.SystemLibrary.line_trace_single_by_profile(world,unreal.Vector(x,y,floor+15),unreal.Vector(x,y,floor-20),'Pawn',True,new+art,unreal.DrawDebugTrace.NONE,True)))
 support.append({'id':row['id'],'floor_cm':floor,'traces':traces,'floor_plane_hit_count':sum(bool(t and t['blocking'] and abs(t['point_cm'][2]-floor)<3) for t in traces),'interpretation':'Five sample diagnostics on existing floor collision; Blender slab rays independently verify support. Local trim/near-wall intersections can obscure this diagnostic.'})
 sides=[('west',(lo[0]-40,cy)),('east',(hi[0]+40,cy)),('north',(cx,hi[1]+40)),('south',(cx,lo[1]-40))]
 for side,(x,y) in sides:
  h=hit(unreal.SystemLibrary.capsule_trace_single_by_profile(world,unreal.Vector(x,y,floor+90),unreal.Vector(x,y,floor+90.1),35,88,'Pawn',True,[],unreal.DrawDebugTrace.NONE,True));clearance.append({'id':row['id'],'side':side,'sample_cm':[x,y,floor+90],'hit':h,'interpretation':'Side-space diagnostic, not a requirement for access on every side or a regulatory clearance.'})
for a in art:assert not a.get_actor_enable_collision();assert str(a.static_mesh_component.get_collision_profile_name())=='NoCollision'
assert hashlib.sha256(pathlib.Path(f['file']).read_bytes()).hexdigest()==f['sha256'];assert hashlib.sha256((P/'Content/Campus/Maps/CampusCenter_R25_R15.umap').read_bytes()).hexdigest()==stage['source_map_sha256']
for path,h in f['original_material_hashes'].items():assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==h
rec={'map':f['map'],'map_sha256':f['sha256'],'all_68_expected_groups_loaded':True,'new_actor_count':len(new),'art_count':len(art),'material_assignments':materials,'support':support,'clearance_candidates':clearance,'original_material_and_baseline_map_hashes_unchanged':True,'scope':'Native property/support/side-capsule diagnostics. Declared export fit is not architectural measurement accuracy. Actual doorway walking and pixel appearance inspection recorded separately.'};(D/'native-properties-r15.json').write_text(json.dumps(rec,indent=2))
