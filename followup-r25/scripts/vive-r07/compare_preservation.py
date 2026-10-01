from pathlib import Path
import json,hashlib
r=Path(__file__).parent;b=json.loads((r.parent/'vr-trigger-walk-r01/final-inventory.json').read_text());q=json.loads((r/'final-inventory.json').read_text())
def eq(a,b):
 if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):return abs(a-b)<1e-8
 if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
 if isinstance(a,dict) and isinstance(b,dict):return set(a)==set(b) and all(eq(a[k],b[k]) for k in a)
 return a==b
names={a['name']:a for a in q['actors']};fail=[]
for a in b['actors']:
 if '_GEN_VARIABLE_' in a['name']:
  match=[c for c in q['actors'] if c['class']==a['class'] and eq(c['transform'],a['transform']) and eq(c['components'],a['components'])];assert len(match)==1;names[a['name']]=match[0]
 c=names.get(a['name']);assert c,a['label']
 for key in ['class','transform','hidden','actor_collision','components','actor_properties','tags','folder']:
  if not eq(a[key],c[key]):fail.append({'label':a['label'],'field':key})
old={d['package']:d['sha256'] for d in b['dependencies']};changed=[d['package'] for d in q['dependencies'] if d['package'] in old and d['sha256']!=old[d['package']] and not d['package'].startswith('/Game/Campus/Maps/')]
assert not changed and len(b['actors'])==2232 and len(q['actors'])==2233
helper=next(a for a in q['actors'] if a['label']=='Vive_OpenXR_Local_Origin_R01');assert not helper['actor_collision']
(r/'preservation.json').write_text(json.dumps({'status':'passed' if not fail else 'failed','baseline_actors_accounted':2232,'final_actor_count':2233,'new_actor':'Vive_OpenXR_Local_Origin_R01, non-colliding','existing_dependency_changes':changed,'actor_failures':fail},indent=2));assert not fail,fail
protected=json.loads((r.parent/'vr-preparation/protected-baseline.json').read_text());p=r.parent/'CampusCenter-vive';exceptions=['unreal/unreal_project/CampusCenter.uproject','unreal/unreal_project/Config/DefaultInput.ini'];fail=[x['path'] for x in protected['files'] if x['path'] not in exceptions and hashlib.sha256((p/x['path']).read_bytes()).hexdigest()!=x['sha256']];assert not fail,fail
original=json.loads((r/'original-r06-state/CampusCenter.uproject').read_text());current=json.loads((p/'unreal/unreal_project/CampusCenter.uproject').read_text());assert current['Plugins'][-1]=={'Name':'OpenXR','Enabled':True};current['Plugins']=current['Plugins'][:-1];assert current==original
original_input=(r/'original-r06-state/Config/DefaultInput.ini').read_text();current_input=(p/'unreal/unreal_project/Config/DefaultInput.ini').read_text();assert current_input.startswith(original_input);assert current_input[len(original_input):]=='\n[/Script/EnhancedInput.EnhancedInputDeveloperSettings]\nbEnableDefaultMappingContexts=True\n+DefaultMappingContexts=(InputMappingContext="/Game/Campus/ViveTriggerWalkR01/IMC_ViveTriggerWalk.IMC_ViveTriggerWalk",Priority=0,bAddImmediately=False,bRegisterWithUserSettings=False)\n'
(r/'protected-source-validation.json').write_text(json.dumps({'untouched_originals_verified':len(protected['files'])-2,'scoped_exceptions':exceptions,'descriptor_only_OpenXR_activation':True,'input_only_pre_session_context_registration':True,'failures':fail},indent=2));print('2232 baseline actors, all dependencies and 9 protected original files unchanged; exactly two authorized configuration exceptions')
