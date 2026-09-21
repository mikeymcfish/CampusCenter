"""Submit an isolated room loop after comparison selects H3."""
from pathlib import Path
import json,requests,sys,time
R=Path(__file__).parent;n=sys.argv[1];D=R/'final'/n;D.mkdir(parents=True,exist_ok=True)
base=json.loads((R/'trials/h3_comfy_endpoints/workflow_api.json').read_text())
start={'108':R.parent/'projection_acrylic_v06/rooms/108/start_image_pilot/iLab_ImageGen_Start.png','102':R/'start_images/102_Commons.png','121':R/'start_images/121_Locker.png','122':R/'start_images/122_Locker.png','GYM':R/'start_images/GYM.png'}[n]
actions={
'108':'Seven students and one teacher in the innovation lab. The two students already standing in clear aisles walk small natural closed loops at a relaxed pace, around the ends of benches. Four students at the right-hand worktables make small hand gestures while handling their existing projects. The student beside the printers watches. The teacher makes one small gesture. Keep exactly two Bambu H2D printers with AMS units in their opening positions and all other machines unchanged.',
'102':'Twelve students in the commons. Four students already standing on clear floor walk short closed paths between the seating groups. Eight seated students read, talk quietly or move their hands a little. Preserve every existing chair, table, sofa and plant and their placement. Walkers go around furniture and give each other room.',
'121':'Six fully clothed students with school bags in the locker room. Two in the upper clear aisle take several relaxed walking steps along small closed paths. Four beside the locker banks make small talking and hand gestures. Everyone stays fully dressed throughout; all locker doors remain closed and fixed. Maintain every locker bank footprint.',
'122':'Six fully clothed students with school bags in the locker room. Two in the upper clear aisle take several relaxed walking steps along small closed paths. Four beside the locker banks make small talking and hand gestures. Everyone stays fully dressed throughout; all locker doors remain closed and fixed. Maintain every locker bank footprint.',
'GYM':'Ten students in complete PE outfits and one teacher in a tracksuit on the gym court. Four students make small relaxed side steps in open court space while the others make subtle arm movements as though preparing a basketball passing drill. The single orange basketball stays with its original holder. The teacher gestures once. Preserve all court markings and side fixtures. No bleachers.'}[n]
prompt=('How the reference pictures align with the target video - Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 12.25-second mark of the target video.\n\n'
'integrated_multimodal_description: [Shot 1] A single static shot from a rigidly fixed orthographic camera looking vertically down. All architecture, furniture, floor markings and black margins remain at identical screen coordinates in every frame. Constant scale, orientation, focus and lighting. Only the existing people move; no camera motion, zoom, perspective change or reframing. '+actions+' Natural alternating footsteps, relaxed arm swings and gentle turns. Remain within clear floor space without crossing furniture, walls or the black room boundary. Keep the same people, clothing and object counts throughout. Movement begins smoothly, follows short closed paths, and returns naturally to the supplied closing poses by the end. No cuts, teleporting, abrupt reversals or newly appearing people. Keep photographic materials and steady contact shadows from the opening image.\n\noverall_soundscape: N/A\n\nnon_diegetic_music: N/A')
url='http://127.0.0.1:8191'
queue=requests.get(url+'/queue',timeout=10).json()
if '--queue-own' in sys.argv:
    assert all(job[3].get('client_id')=='campus-r12-experiments' for job in queue['queue_running']+queue['queue_pending']), 'A different client owns a queued job'
else:
    assert not queue['queue_running'] and not queue['queue_pending'],'Wait for current GPU job before submitting'
assert not (D/'status.json').exists(),'Existing submission: inspect status before resubmitting'
with start.open('rb') as f:
    r=requests.post(url+'/upload/image',files={'image':(f'r12_room_{n}_start.png',f,'image/png')},data={'subfolder':'r12_experiments','overwrite':'false'},timeout=60);r.raise_for_status();im=r.json()
file=im['subfolder']+'/'+im['name'];state=json.loads(base['153']['inputs']['h3_data'])
state.update(width=768,height=768,length=294,prompt=prompt.replace('Picture 1','@first').replace('Picture 2','@last'));state['slots']['first']={'file':file};state['slots']['last']={'file':file}
base['153']['inputs']['h3_data']=json.dumps(state);base['149']['inputs']['filename_prefix']=f'final/Room_{n}_H3_Loop'
(D/'Prompt.txt').write_text(prompt,encoding='ascii');(D/'workflow_api.json').write_text(json.dumps(base,indent=2));(D/'start_source.txt').write_text(str(start))
r=requests.post(url+'/prompt',json={'prompt':base,'client_id':'campus-r12-experiments'},timeout=60);(D/'submission.json').write_text(r.text);r.raise_for_status()
(D/'status.json').write_text(json.dumps({'status':'queued','prompt_id':r.json()['prompt_id'],'server':url,'started':time.time()},indent=2));print(r.text)
