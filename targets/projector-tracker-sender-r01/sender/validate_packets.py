from pathlib import Path
import json,math,hashlib
r=Path(__file__).parent
packets=json.loads((r/'osc-pie-r03-capture.json').read_text())
fixture=json.loads((r/'sender-pie-validation.json').read_text())
expected={'ground':(0,1),'roomscale-tall-gym':(0,1),'upper':(1,1),'focus-loss':(-1,0),'focus-recovery':(1,1),'unsupported':(-1,0)}
checks={}
checks['exact_wire']=all(p['address']=='/campuscenter/player/v1' and p['types']==',issisfffffiii' and p['args'][0]==1 and p['args'][1]=='campuscenter-r29-p02-sample-1-250-v1' and p['source'][0]=='127.0.0.1' for p in packets)
checks['first_session_sequence_teleport']=packets[0]['args'][3]==0 and packets[0]['args'][12]==1 and packets[0]['args'][2].startswith('ue-')
checks['sequence']=all(b['args'][3]==a['args'][3]+1 and b['args'][2]==a['args'][2] for a,b in zip(packets,packets[1:]))
checks['utc_decimal_fresh']=all(str(p['args'][4]).isdigit() and -1000<=p['utc_ms']-int(p['args'][4])<=500 for p in packets)
checks['registration_finite']=all(all(math.isfinite(v) for v in p['args'][5:10]) and abs(p['args'][7]-(p['args'][5]+4700)/25)<.05 and abs(p['args'][8]-(-p['args'][6]+230)/25)<.05 for p in packets)
rows=[]
for case in fixture['cases']:
    sample=[p for p in packets if case['start']+.25<=p['monotonic']<=case['end']]
    correct=bool(sample) and all(tuple(p['args'][10:12])==expected[case['name']] for p in sample)
    camera=case['manager'];xy_match=bool(sample) and abs(sample[-1]['args'][5]-camera[0])<.02 and abs(sample[-1]['args'][6]-camera[1])<.02
    rows.append(dict(name=case['name'],packets=len(sample),expected=expected[case['name']],state_pass=correct,camera_xy_pass=xy_match))
checks['six_floor_camera_cases']=all(x['state_pass'] and x['camera_xy_pass'] for x in rows)
tall=next(c for c in fixture['cases'] if c['name']=='roomscale-tall-gym')
checks['tall_ground_camera_above_upper']=tall['camera'][2]>426.72 and abs(tall['camera'][0]-tall['pawn'][0])>100
rate=(len(packets)-1)/(packets[-1]['monotonic']-packets[0]['monotonic'])
checks['nominal_20hz']=19<=rate<=21
report=dict(passed=all(checks.values()),packets=len(packets),rate_hz=rate,checks=checks,cases=rows,scope=fixture['scope'],shipping_final_rebuild_pending=True,packaged_receiver_acceptance_pending=True)
(r/'osc-wire-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
assert report['passed']
