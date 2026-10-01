import unreal,pathlib,json
R=pathlib.Path(__file__).parent/'combined_r01/trophies';E=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();S=unreal.EditorStaticMeshLibrary;rows=[]
for name,files in [('SilverCup',[R/'cup_merged'/f'SilverCup_Assembly_LOD{i}.glb' for i in range(3)]),('RegionalPlaque',[R/'plaque_merged/RegionalPlaque_Assembly.glb'])]:
 meshes=[]
 for i,f in enumerate(files):
  dest=f'/Game/Campus/TrophiesTR27R01/Import/{name}/LOD{i}';t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=dest;t.automated=True;t.save=True;T.import_asset_tasks([t]);found=[unreal.load_asset(p) for p in E.list_assets(dest,recursive=True)];m=[a for a in found if isinstance(a,unreal.StaticMesh)];assert len(m)==1;meshes.append(m[0])
 dest=f'/Game/Campus/TrophiesTR27R01/Runtime/{name}_TR27R01';n=unreal.load_asset(dest) or E.duplicate_asset(meshes[0].get_path_name(),dest);assert n
 for i,m in enumerate(meshes[1:],1):unreal.log(str(S.set_lod_from_static_mesh(n,i,m,0,True)))
 nan=n.get_editor_property('nanite_settings');nan.enabled=False;n.set_editor_property('nanite_settings',nan);n.set_editor_property('asset_import_data',unreal.AssetImportData(outer=n,name='PortableProvenance'));E.save_loaded_asset(n,only_if_is_dirty=False)
 d=n.get_static_mesh_description(0);p=[d.get_vertex_position(unreal.VertexID(id_value=i)).to_tuple() for i in range(d.get_vertex_count())];bounds=[[min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)]]
 rows.append({'name':name,'asset':n.get_path_name(),'bounds_cm':bounds,'lod_count':S.get_lod_count(n),'triangles':[n.get_static_mesh_description(i).get_triangle_count() for i in range(S.get_lod_count(n))]})
(R/'native-assets.json').write_text(json.dumps(rows,indent=2));unreal.SystemLibrary.quit_editor()


