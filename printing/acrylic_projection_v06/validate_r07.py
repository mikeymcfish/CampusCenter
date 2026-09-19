from pathlib import Path
import json,re,hashlib,urllib.request
from PIL import Image
R=Path(__file__).parent
packs=json.loads((R/'rooms/reference_packs.json').read_text())
maps=json.loads((R/'projection/map.json').read_text())
headings=['subject_definitions:','summary:','retention_analysis:','detailed_description:','overall_soundscape:','non_diegetic_music:']
assert len(packs)==31 and maps['speed_px_per_second']==40
for p in packs:
    d=R/'rooms'/p['room'];prompt=(d/'H3_Loop_Prompt.txt').read_text(encoding='utf-8')
    assert 2<=len(p['references'])<=9 and len(prompt)<=7000
    assert [x for x in prompt.splitlines() if x in headings]==headings
    assert '[reference generation]' in prompt and '[Shot 1]' in prompt
    assert len(re.findall(r'^<Subject \d+>:',prompt,re.M))==2*len(p['references'])
    for i,r in enumerate(p['references'],1):
        f=d/r['file'];assert f.is_file();Image.open(f).verify()
        assert f'<Picture {i}>' in prompt
        url='http://127.0.0.1:8769/rooms/'+p['room']+'/'+r['file']
        with urllib.request.urlopen(url) as response: assert response.status==200
    assert (d/'References.html').is_file()
assert next(p for p in packs if p['room']=='108')['count']==9
for r in maps['rooms']:
    assert r['image'].startswith('cinematic/') and 'Room_3D' not in r['image']
    Image.open(R/'projection'/r['image']).verify()
demo=json.loads((R/'projection/examples/explorer_validation.json').read_text())
assert demo['all_frames_blackout'] and demo['first_last_identical'] and demo['seconds']<33
result={'revision':'r07','room_packs':31,'total_reference_assignments':sum(p['count'] for p in packs),'ilab_references':9,'max_prompt_characters':max(p['prompt_chars'] for p in packs),'all_reference_images_reopened':True,'all_reference_urls_http_200':True,'gym_assignments':31,'unique_imagegen_images':len(set(r['image'] for r in maps['rooms'])),'blender_gym_images':0,'walking_default_px_per_second':40,'explorer_seconds':demo['seconds'],'h3_generation_submitted':False}
(R/'revision_07_validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
