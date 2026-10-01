from pathlib import Path
r=Path(__file__).parent;base=r.parent/'vr-trigger-walk-r01'
s=(base/'test_input.py').read_text().replace('CampusCenter_Vive_EQ27_R06_TriggerWalk','CampusCenter_Vive_EQ27_R07_OpenXR')
s=s.replace("report={'method':", "raw_cases=list(cases);cases=raw_cases+[(name+'_OpenXRInjection',duration,la,lc,ra,rc,focus,lt,rt,yaw,expected) for name,duration,la,lc,ra,rc,focus,lt,rt,yaw,expected in raw_cases]\nreport={'method':")
s=s.replace('assert helper.diagnostic_frame(la,lc,ra,rc,focused,lt,rt,yaw)',"if name.endswith('_OpenXRInjection'):\n   origin=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.Actor) if a.get_class().get_path_name()=='/Script/CampusCrowdFix.CampusViveXROrigin')\n   assert helper.diagnostic_frame(0,False,0,False,focused,lt,rt,yaw)\n   assert origin.diagnostic_inject(max(la,float(lc)),max(ra,float(rc)))\n  else:assert helper.diagnostic_frame(la,lc,ra,rc,focused,lt,rt,yaw)")
(r/'test_input.py').write_text(s)
(r/'test_keyboard.py').write_text((base/'test_keyboard.py').read_text().replace('CampusCenter_Vive_EQ27_R06_TriggerWalk','CampusCenter_Vive_EQ27_R07_OpenXR'))
s=(base/'snapshot_after.py').read_text().replace('vr-trigger-walk-r01','vr-openxr-r07-r01').replace('CampusCenter_Vive_EQ27_R06_TriggerWalk','CampusCenter_Vive_EQ27_R07_OpenXR');(r/'snapshot_after.py').write_text(s)
s=(base/'package_review.ps1').read_text().replace('review_build_vive_trigger_r06_r01','review_build_vive_openxr_r07_r01').replace('staging-r06-r01','staging-r07-r01');(r/'package_review.ps1').write_text(s)
s=(base/'smoke_normal.py').read_text().replace('review_build_vive_trigger_r06_r01','review_build_vive_openxr_r07_r01').replace("'-game','-fullscreen'","'-game','-vr','-fullscreen'");(r/'smoke_normal.py').write_text(s)
s=(base/'packaged_capture_one.py').read_text().replace('review_build_vive_trigger_r06_r01','review_build_vive_openxr_r07_r01').replace('CampusCenter_Vive_EQ27_R06_TriggerWalk','CampusCenter_Vive_EQ27_R07_OpenXR').replace("'-windowed','-ResX=1280'","'-vr','-windowed','-ResX=1280'");(r/'packaged_capture_one.py').write_text(s)
(r/'packaged_capture.py').write_text((base/'packaged_capture.py').read_text())
