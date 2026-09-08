import unreal,pathlib
root=pathlib.Path(unreal.Paths.project_dir())
for script in ['fix_fabric_v03.py','polish_v03.py','native_surfaces_v03.py','world_mapping_v03.py']:
 exec((root/script).read_text())
