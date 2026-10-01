import json,pathlib
O=pathlib.Path(__file__).parent
R=pathlib.Path('C:/Users/mikef/Documents/Codex/2026-09-30/task/CampusCenter-new-plans/downstream/furniture_art_v26_r01')
data=json.loads((R/'native-properties-r15.json').read_text());matches=[]
ids=['FA26_PH02_Fitness218_'+n for n in ('027','029','030')]
def walk(o,path='root'):
 if isinstance(o,dict):
  if (o.get('label') in ids and 'actor' in o) or (o.get('actor') in ids and 'material' in o):matches.append({'evidence_path':path,'record':o})
  for k,v in o.items():walk(v,path+'/'+k)
 elif isinstance(o,list):
  for i,v in enumerate(o):walk(v,path+'/'+str(i))
walk(data)
(O/'native_integration_evidence.json').write_text(json.dumps({'source':str(R/'native-properties-r15.json'),'matches':matches},indent=2))
print([(x['record'].get('label'),x['record'].get('actor')) for x in matches if 'label' in x['record']])
