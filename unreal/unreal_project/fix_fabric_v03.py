import pathlib,unreal
root=pathlib.Path(unreal.Paths.project_dir())
code=(root/'polish_materials_v02.py').read_text().split('# Preserve')[0]
exec(code.replace("'RGB'","''").replace("'Coordinates'","'UVs'"))
