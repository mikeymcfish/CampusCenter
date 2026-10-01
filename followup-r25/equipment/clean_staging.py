import bpy,pathlib
O=pathlib.Path(__file__).parent
bpy.data.orphans_purge(do_recursive=True)
bpy.context.scene.camera=None
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CampusCenter_Equipment_Editable_EQ27_R01.blend'))
print('CLEAN_SAVED',len(bpy.data.objects),len(bpy.data.meshes))
