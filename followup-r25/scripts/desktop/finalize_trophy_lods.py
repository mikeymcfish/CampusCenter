import unreal,pathlib,json
R=pathlib.Path(__file__).parent/'combined_r01/trophies';S=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);E=unreal.EditorAssetLibrary;assert S
rows=json.loads((R/'native-assets.json').read_text())
for row in rows:
 n=unreal.load_asset(row['asset'])
 if row['name']=='SilverCup':
  for i in [1,2]:
   assets=[unreal.load_asset(p) for p in E.list_assets(f'/Game/Campus/TrophiesTR27R01/Import/SilverCup/LOD{i}',recursive=True)];m=next(a for a in assets if isinstance(a,unreal.StaticMesh));result=S.set_lod_from_static_mesh(n,i,m,0,True);assert result==i,result
  assert S.get_lod_count(n)==3
 row['lod_count']=S.get_lod_count(n);row['triangles']=[n.get_static_mesh_description(i).get_triangle_count() for i in range(row['lod_count'])];assert E.save_loaded_asset(n,only_if_is_dirty=False)
assert rows[0]['triangles']==[23312,12750,5252];assert rows[1]['triangles']==[3964];(R/'native-assets.json').write_text(json.dumps(rows,indent=2))
exec((pathlib.Path(__file__).parent/'place_trophies.py').read_text())
