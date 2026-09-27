import collections,re
original=json.loads((R/'actors.json').read_text())
def signature(row):
 rotation=tuple(round(float(x),3) for x in re.findall(r'(?:pitch|yaw|roll): ([\d.\-]+)',row['rotation']))
 return (row['label'],row['class'],tuple(round(x,3) for x in row['location']),rotation,tuple(round(x,3) for x in row['scale']),tuple((c['mesh'],tuple(c['materials'])) for c in row['components'] if not c['mesh'].startswith('/Engine/EditorMeshes/')))
def current_row(a):
 return {'label':a.get_actor_label(),'class':a.get_class().get_name(),'location':vec(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'scale':vec(a.get_actor_scale3d()),'components':[{'mesh':c.static_mesh.get_path_name(),'materials':[m.get_path_name() if m else None for m in c.get_materials()]} for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.static_mesh]}
original_protected=collections.Counter(signature(row) for row in original if not re.fullmatch(r'DD_Trophy_\d\d',row['label']))
current=[current_row(a) for a in A.get_all_level_actors()]
current_protected=collections.Counter(signature(row) for row in current if not row['label'].startswith('PS08_') and not re.fullmatch(r'DD_Trophy_\d\d',row['label']))
missing=list((original_protected-current_protected).elements())
unexpected=list((current_protected-original_protected).elements())
result={'original_actors':len(original),'current_actors':len(current),'protected_original_actors':sum(original_protected.values()),'missing_or_changed_protected':missing,'unexpected_nonaddition':unexpected,'new_prop_parts':sum(row['label'].startswith(('PS08_laptops','PS08_cups')) for row in current),'bleacher_parts':sum(row['label'].startswith('PS08_Bleacher') for row in current)}
(R/'preservation.json').write_text(json.dumps(result,indent=2))
assert not missing and not unexpected,result
assert result['new_prop_parts']==24
L.eject_pilot_level_actor()
assert L.save_current_level()
(R/'saved.json').write_text(json.dumps({'map':'/Game/Campus/Maps/CampusCenter_StandardAssets_v07','saved':True,'validation':result},indent=2))
