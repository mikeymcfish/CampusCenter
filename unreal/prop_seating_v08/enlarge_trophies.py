import re
for a in A.get_all_level_actors():
 if not re.fullmatch(r'DD_Trophy_\d\d',a.get_actor_label()):continue
 o,e=a.get_actor_bounds(False);base=o.z-e.z;s=a.get_actor_scale3d()
 a.set_actor_scale3d(unreal.Vector(s.x,s.y*1.45,s.z*1.45))
 no,ne=a.get_actor_bounds(False)
 a.set_actor_location(a.get_actor_location()+unreal.Vector(o.x-no.x,o.y-no.y,base-(no.z-ne.z)),False,False)
 final,fe=a.get_actor_bounds(False)
 report['trophies'].append({'label':a.get_actor_label(),'factor':1.45,'base_before':base,'base_after':final.z-fe.z,'height_cm':fe.z*2,'width_cm':fe.y*2})
assert len(report['trophies'])==10
(R/'trophies_report.json').write_text(json.dumps(report['trophies'],indent=2))
