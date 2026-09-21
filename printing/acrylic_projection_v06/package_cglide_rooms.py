"""Repair portable prompt text and pack the current room refs for CGlide."""
from pathlib import Path
from datetime import datetime,timezone
import json,zipfile,hashlib,re,html,shutil,unicodedata
R=Path(__file__).parent
O=R/'cglide';O.mkdir(exist_ok=True)
B=R/'revision_09_before';B.mkdir(exist_ok=True)
packs=json.loads((R/'rooms/reference_packs.json').read_text(encoding='utf-8'))
rooms={r['number']:r for r in json.loads((R/'rooms/room_contract.json').read_text())}

def plain(s):
    # The canonical files are UTF-8; the supplied pasted text showed a browser
    # decoding error. Preserve wording and use robust ASCII punctuation.
    replace={'\u2014':' - ','\u2013':'-','\u2018':"'",'\u2019':"'",'\u201c':'"','\u201d':'"','\u2026':'...','\u00d7':'x','\u00b7':' / ','\u2192':'->','\u00a0':' ','\ufeff':''}
    for old,new in replace.items():s=s.replace(old,new)
    s=unicodedata.normalize('NFKD',s).encode('ascii','strict').decode('ascii')
    return s

for p in (R/'rooms').rglob('*'):
    if p.suffix.lower() not in ['.md','.txt']:continue
    old=p.read_text(encoding='utf-8-sig');new=plain(old)
    if old!=new:
        target=B/p.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():shutil.copy2(p,target)
        p.write_text(new,encoding='utf-8',newline='\n')

asset_by_hash={};assets={};records=[];shots=[]
for pack in sorted(packs,key=lambda p:(p['room']=='GYM',p['room'])):
    n=pack['room'];D=R/'rooms'/n;name=plain(rooms[n]['name'])
    prompt=(D/'H3_Loop_Prompt.txt').read_text(encoding='utf-8')
    pack['prompt_chars']=len(prompt)
    # CGlide aligns frame counts to 17k+5. 294 is the first such count >=288.
    cp=prompt.replace('12-second','12.25-second').replace('12 seconds','12.25 seconds')
    cp=cp.replace('<Picture 1>','@first')
    slots=[];ref_info=[]
    for i,ref in enumerate(pack['references'][:1],1):
        f=D/ref['file'];raw=f.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha not in asset_by_hash:
            file=f'r{n}_p{i:02d}_{f.name}'
            assert file not in assets
            asset_by_hash[sha]=file;assets[file]=f
        file=asset_by_hash[sha];slots.append({'file':file})
        ref_info.append({'slot':i,'title':plain(ref['title']),'role':plain(ref['role']),'asset':file,'sha256':sha,'source':f.relative_to(R).as_posix()})
    assert len(slots)==1 and cp.isascii() and len(cp)<7000
    ref_info[0]['slot']='first';ref_info[0]['role']='Exact opening frame; no semantic appearance references'
    state={'mode':'fl2va','width':768,'height':768,'length':294,'ref_image_size':'match','pace':2.5,'prompt':cp,'slots':{'first':slots[0],'last':{},'images':[{} for _ in range(9)],'videos':[{}, {}, {}],'audios':[{}, {}, {}]},'cont':{}}
    shot={'id':f'campus-ground-room-{n}','name':f'{n} - {name}','off':False,'state':state}
    shots.append(shot)
    stem=f'Room_{n}_{re.sub(r"[^A-Za-z0-9]+","_",name).strip("_")}.h3proj.zip'
    records.append({'room':n,'name':name,'package':stem,'refs':ref_info,'mask':f'rooms/{n}/Room_Mask_1024.png'})

instructions='''Campus Center ground-floor room loops - CGlide packed projects

IMPORT: In CGlide H3 Studio, use Project > Open and choose a .h3proj.zip.
Use Project Open, not the top-bar Load button for a single-clip state pack.
The combined project contains 31 independent room shots. Individual packages
contain one room each. Reference images are embedded and already assigned;
there are no missing reference slots to fill. No video/audio references or
continuation links are set. Do not enable Carry/Chain between these rooms.

Mode: ref2va. Local checkpoint: H3-Base-Ref2VA.
Output: 768 x 768, 24 fps, 294 frames (12.25 seconds).
Your installed CGlide requires a 17k+5 frame count; 294 is its next legal
count above 12 seconds. Packed prompts describe a full 12.25-second loop,
with no frozen tail. The ordinary downloadable H3 text remains 12 seconds.
Preserve the complete loop duration when playing it back.

Image slot 1 controls exact overhead layout, positions and room boundaries.
Remaining slots transfer only their stated appearance/details. They must
not override camera, location, furniture placement or geometry. The iLab
includes all nine references and exactly two Bambu H2D + AMS 2 Pro printers.
Prompts include natural student walking where appropriate, fixed light,
fixed vertical camera and safe clear paths. The gym uses the updated
reference without bleachers. No generation has been run.

The masks/ folder holds post-generation masks; these are not image slots.
Reapply the matching room mask after generation and inspect motion, object
counts and the loop seam before projection. H3 does not guarantee exact
pixels or seamless movement. The original architectural sources are unchanged.

Prompt source: manual official-format rewrite.
'''
instructions='''Revision 11 - overhead first-frame image-to-video
Import with H3 Studio > Project > Open. Reopen the downloaded project to
replace previously loaded shots; opening the web page does not update them.
CGlide mode: FL2VA with FIRST populated and LAST empty (image-to-video).
Required installed diffusion model: minimax_h3_fl2va_pruned_int8_convrot.safetensors
Video VAE: minimax_h3_video_vae_fp16.safetensors
Audio VAE: minimax_h3_audio_vae_fp32.safetensors
Select the FL2VA diffusion model in the ComfyUI workflow yourself; project
imports do not change the external model loader. Do not use the Ref2VA model.
Only the exact overhead opening image is embedded. Appearance/product
references have been removed from conditioning; their details are in prose.
768 x 768, 24 fps, 294 frames / 12.25 seconds. Do not enable Carry/Chain.
Static camera requested; first-frame conditioning does not guarantee a fixed
camera throughout or a seamless loop. No generation was submitted or tested.
Existing people in the opening image provide the best motion starting point;
additional requested people may emerge gradually if absent in the image.
Masks are post-generation files, not conditioning inputs. Masking does not
correct internal camera drift. Inspect results before using for projection.
Prompt source: manual official-format rewrite.
'''
(O/'IMPORT_INSTRUCTIONS.txt').write_text(instructions,encoding='ascii')

def write_project(filename,title,selected):
    project={'meta':{'app':'H3 Studio project','version':1,'packed':True,'shots':len(selected),'saved':datetime.now(timezone.utc).isoformat()},'name':title,'idx':0,'shots':selected}
    needed={shot['state']['slots']['first']['file'] for shot in selected}
    selected_ids={s['id'].rsplit('-',1)[-1] for s in selected}
    with zipfile.ZipFile(O/filename,'w',compression=zipfile.ZIP_STORED,allowZip64=False) as z:
        z.writestr('project.json',json.dumps(project,ensure_ascii=True,indent=1))
        z.writestr('README.txt',instructions)
        z.writestr('REFERENCE_ORDER.json',json.dumps([r for r in records if r['room'] in selected_ids],ensure_ascii=True,indent=2))
        for file in sorted(needed):z.write(assets[file],'assets/'+file)
        for n in sorted(selected_ids):z.write(R/'rooms'/n/'Room_Mask_1024.png',f'masks/{n}_Room_Mask_1024.png')
    with zipfile.ZipFile(O/filename) as z:
        assert z.testzip() is None
        reopened=json.loads(z.read('project.json'))
        assert reopened==project
        for file in needed:assert hashlib.sha256(z.read('assets/'+file)).digest()==hashlib.sha256(assets[file].read_bytes()).digest()
    return (O/filename).stat().st_size

for shot,record in zip(shots,records):record['bytes']=write_project(record['package'],f'Campus Center - {record["room"]} {record["name"]} - Overhead Loop',[shot])
combined='Campus_Center_Ground_Floor_All_Rooms.h3proj.zip'
combined_bytes=write_project(combined,'Campus Center - Ground Floor Projection Loops',shots)
cards=''.join(f'<tr><td>{r["room"]}</td><td>{html.escape(r["name"])}</td><td>{len(r["refs"])}</td><td><a href="{r["package"]}" download>Download project ({r["bytes"]/1e6:.1f} MB)</a></td><td><a href="../rooms/{r["room"]}/References.html">View references</a></td></tr>' for r in records)
(O/'index.html').write_text(f'<!doctype html><meta charset="utf-8"><title>Campus Center CGlide projects</title><style>body{{font:16px system-ui;background:#0a1720;color:#e8f2f5;margin:32px;max-width:1100px}}a{{color:#81e4ce}}p{{line-height:1.6}}table{{border-collapse:collapse;width:100%}}td,th{{padding:12px;text-align:left;border-bottom:1px solid #2c404d}}.download{{padding:15px;background:#173d3a;border-radius:8px;display:inline-block}}small{{color:#afc4cf}}</style><h1>CGlide room project packages</h1><p>31 ground-floor rooms. Each package includes its prompt, assigned reference images and projection mask. Import with <strong>H3 Studio &gt; Project &gt; Open</strong>.</p><p><a class="download" href="{combined}" download>Download all 31 rooms as one project ({combined_bytes/1e6:.1f} MB)</a></p><p>768 x 768 / 24 fps / 294 frames (12.25 seconds). No generation has been run. <a href="IMPORT_INSTRUCTIONS.txt">Import and playback notes</a> / <a href="../rooms/">Room reference gallery</a></p><table><thead><tr><th>Room</th><th>Area</th><th>References</th><th>Individual package</th><th>Preview</th></tr></thead><tbody>{cards}</tbody></table>',encoding='utf-8')

for record in records:
    D=R/'rooms'/record['room'];href='../../cglide/'+record['package']
    p=D/'References.html';s=p.read_text(encoding='utf-8')
    if 'CGlide project package' not in s:s=s.replace('<main>',f'<p><a href="{href}" download>Download CGlide project package</a> / <a href="../../cglide/">All CGlide projects</a></p><main>')
    s=s.replace('href="H3_Loop_Prompt.txt"','href="Prompt.html"')
    p.write_text(s,encoding='utf-8')
    prompt=(D/'H3_Loop_Prompt.txt').read_text(encoding='utf-8')
    page='''<!doctype html><meta charset="utf-8"><title>Room ROOM H3 prompt</title><style>body{font:16px system-ui;background:#0a1720;color:#e6f2f5;margin:28px;max-width:1150px}a{color:#83e4cc}button{background:#1b4a43;color:white;border:1px solid #76d3bd;border-radius:7px;padding:10px 20px;font:inherit;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#132633;padding:22px;line-height:1.65;font:14px/1.65 Consolas,monospace}p{line-height:1.6}</style><h1>Room ROOM - H3 prompt</h1><p><button id="copy">Copy prompt</button> <span id="status"></span> / <a href="H3_Loop_Prompt.txt" download>Download plain text</a> / <a href="References.html">Reference images</a> / <a href="PACKAGE" download>CGlide project</a></p><p>This portable H3 prompt uses 12 seconds. The CGlide package uses its required 294-frame grid (12.25 seconds), with matching prompt timing.</p><pre id="prompt">PROMPT</pre><script>document.getElementById('copy').onclick=async()=>{try{await navigator.clipboard.writeText(document.getElementById('prompt').textContent);document.getElementById('status').textContent='Copied';}catch(e){document.getElementById('status').textContent='Select and copy the text below.';}};</script>'''
    page=page.replace('ROOM',record['room']).replace('PACKAGE',href).replace('PROMPT',html.escape(prompt))
    (D/'Prompt.html').write_text(page,encoding='utf-8')
    p=D/'References.md';s=p.read_text(encoding='utf-8')
    if 'CGlide project package' not in s:s+=f'\n[CGlide project package]({href}) - references preassigned; 768 x 768, 294 frames / 12.25 seconds. Import with Project > Open. [All packages](../../cglide/index.html).\n'
    p.write_text(s,encoding='utf-8')
(R/'rooms/reference_packs.json').write_text(json.dumps(packs,indent=2),encoding='utf-8')
for p in [R/'README.md',R/'rooms/README.md']:
    s=p.read_text(encoding='utf-8-sig')
    if '## CGlide packages and text encoding' not in s:s+='\n## CGlide packages and text encoding\n\nThe cglide folder contains 31 individual .h3proj.zip files and one combined project, with images embedded and already assigned. Open cglide/index.html for downloads. Use H3 Studio > Project > Open. Local CGlide settings: ref2va, 768 x 768, 24 fps, 294 frames (12.25 seconds, required frame grid). Packed prompts match that loop duration; ordinary H3 prompts remain 12 seconds. Text prompts and reference instructions use plain punctuation, and the server explicitly declares UTF-8. No generation was run.\n'
    p.write_text(s,encoding='utf-8')
manifest={'room_count':31,'packages':records,'combined_package':combined,'combined_bytes':combined_bytes,'unique_embedded_images':len(assets),'total_image_assignments':sum(len(r['refs']) for r in records),'generation_submitted':False}
notice='<p><strong>Revision 11: first-frame image-to-video.</strong> Only the overhead opening image is included. Appearance references are removed; details are in the prompt. Select <code>minimax_h3_fl2va_pruned_int8_convrot.safetensors</code> in the diffusion-model loader. CGlide FL2VA mode has only FIRST filled. Reimport the new package with Project &gt; Open.</p>'
p=O/'index.html';s=p.read_text(encoding='utf-8');s=s.replace('<h1>CGlide room project packages</h1>','<h1>CGlide room project packages</h1>'+notice);p.write_text(s,encoding='utf-8')
for record in records:
    for filename in ['Prompt.html','References.html']:
        p=R/'rooms'/record['room']/filename;s=p.read_text(encoding='utf-8')
        if 'Revision 11: first-frame' not in s:s=s.replace('</h1>','</h1>'+notice,1)
        p.write_text(s,encoding='utf-8')
for p in [R/'README.md',R/'rooms/README.md']:
    s=p.read_text(encoding='utf-8')
    s=s.split('## CGlide packages and text encoding')[0]+'## CGlide packages and text encoding\n\n'+instructions
    p.write_text(s,encoding='utf-8')
(O/'package_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k!='packages'},indent=2))
