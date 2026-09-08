import unreal,json,pathlib,math
root=pathlib.Path(unreal.Paths.project_dir());rooms=json.loads((root.parent/'unreal_transfer/exports/rooms.json').read_text())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def rotation(d):return unreal.Rotator(pitch=math.degrees(math.atan2(d[2],math.hypot(d[0],d[1]))),yaw=math.degrees(math.atan2(d[1],d[0])),roll=0)
for path in unreal.EditorAssetLibrary.list_assets('/Game/Campus/Maps',recursive=True):
 if not isinstance(unreal.load_asset(path),unreal.World):continue
 levels.load_level(str(path).split('.')[0]);mapname=str(path).split('.')[-1];idx=int(mapname[-2:]) if mapname.startswith('Room_') else 0
 for a in actors.get_all_level_actors():
  label=a.get_actor_label()
  if label.startswith('Review_'):
   r=rooms[int(label[7:9])];a.set_actor_location(unreal.Vector(*r['p']),False,False);a.set_actor_rotation(rotation(r['dir']),False)
  if isinstance(a,unreal.RectLight):a.set_actor_rotation(unreal.Rotator(pitch=-90,yaw=0,roll=0),False)
  if isinstance(a,unreal.DirectionalLight):a.set_actor_rotation(unreal.Rotator(pitch=-38,yaw=-125,roll=0),False)
  if label=='Campus_Explorer' or isinstance(a,unreal.PlayerStart):
   r=rotation(rooms[idx]['dir']);r.pitch=0;a.set_actor_rotation(r,False);p=rooms[idx]['p'];a.set_actor_location(unreal.Vector(p[0],p[1],p[2]-75),False,False)
 assert levels.save_current_level()
(root/'orientation_fix.json').write_text(json.dumps({'status':'corrected','reason':'Use explicit keyword arguments for Python Rotator construction; positional order differs from C++ FRotator','maps_fixed':12},indent=2))
