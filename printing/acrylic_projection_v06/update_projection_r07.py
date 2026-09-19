from pathlib import Path
import json, shutil, html, re

R = Path(__file__).parent
W = R.parent
P = R / 'projection'
backup = R / 'revision_07_before'
backup.mkdir(exist_ok=True)

def save_before(path):
    target = backup / path.relative_to(R)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists(): shutil.copy2(path, target)

def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

photos = {
    'entrance.png': W/'guiding_references_v20/01_entrance_00s.png',
    'lab_detail.png': W/'guiding_references_v20/02_ilab_03s.png',
    'athletics.png': W/'guiding_references_v20/03_athletics_corridor_06s.png',
    'commons.png': W/'output_v9/walkthrough/segment_01_middle_realistic_v2.png',
}
for name, src in photos.items(): copy(src, P/'cinematic'/name)
assert (P/'cinematic/ilab_wide.png').exists()
map_path=P/'map.json'; save_before(map_path)
m=json.loads(map_path.read_text())
m['speed_px_per_second']=40
m['revision']='r07 cinematic references and faster walking'

def cinematic(n):
    if n=='108': return 'ilab_wide.png', 'IMAGEGEN / INNOVATION LAB', True
    if n in ['100','103','104','114']: return 'entrance.png', 'IMAGEGEN / ENTRANCE' if n=='100' else 'RELATED VIEW / ENTRANCE', n=='100'
    if n in ['101','102','105','106','110','111','112','113']: return 'commons.png', 'IMAGEGEN / COMMONS' if n=='102' else 'RELATED VIEW / COMMONS', n=='102'
    if n=='109': return 'lab_detail.png', 'RELATED VIEW / LAB DETAIL', False
    return 'athletics.png', 'RELATED VIEW / ATHLETICS CORRIDOR', False

for room in m['rooms']:
    photo, caption, exact = cinematic(room['number'])
    room.update(image='cinematic/'+photo, image_caption=caption, image_is_room_specific=exact)
map_path.write_text(json.dumps(m,indent=2),encoding='utf-8')

js_path=P/'player.js';save_before(js_path);js=js_path.read_text(encoding='utf-8')
js=js.replace('const illustrations=new Map()', 'let speed=40;\nconst illustrations=new Map()')
js=js.replace('function step(dx,dy){let did=false;', 'function stepOnce(dx,dy){let did=false;')
js=js.replace('function reset(){', "function step(dx,dy){const count=Math.max(1,Math.ceil(Math.hypot(dx,dy)/.5));for(let i=0;i<count;i++)stepOnce(dx/count,dy/count)}\nfunction reset(){")
js=js.replace('dx/mag*20*dt,dy/mag*20*dt','dx/mag*speed*dt,dy/mag*speed*dt').replace('remaining=20*dt','remaining=speed*dt')
js=js.replace('step(dx*.8,dy*.8)','step(dx*speed*.04,dy*speed*.04)')
js=js.replace("g.fillText('ROOM CUTAWAY · EXISTING MODEL',x+12,y+h-9)","wrapText(r.image_caption,x+12,y+h-9,w-24,9)")
js=js.replace('its 3D illustration','a cinematic ImageGen reference')
js=js.replace('31 room images','31 cinematic assignments')
js=js.replace('Canvas: ${canvas.width}', 'Speed: ${speed/20}× original (${speed} px/s)\\nCanvas: ${canvas.width}')
js=js.replace("try{map=await(await fetch('map.json')).json();", "$('#speed').onchange=()=>{speed=Number($('#speed').value);canvas.focus();updateStatus()};\ntry{map=await(await fetch('map.json')).json();speed=map.speed_px_per_second;$('#speed').value=String(speed);")
js_path.write_text(js,encoding='utf-8')
index=P/'index.html';save_before(index);s=index.read_text(encoding='utf-8')
s=s.replace('its 3D illustration','a cinematic ImageGen reference').replace('/ GROUND FLOOR / v06','/ GROUND FLOOR / v06 · r07')
s=s.replace('<label for="destination">', '<label for="speed">Walking speed</label><select id="speed"><option value="20">1× · original</option><option value="40" selected>2× · faster</option><option value="60">3× · fast</option><option value="80">4× · quickest</option></select><label for="destination">')
s=s.replace('<a href="README.md">Setup', '<a href="../rooms/">Room prompts and reference packs</a><br><a href="README.md">Setup')
index.write_text(s,encoding='utf-8')

equipment=W/'output_v9/equipment/references'
commons_source=Path('C:/Users/mikef/Documents/Campus Center/vlcsnap-2026-09-06-09h21m09s397.png')
shared=R/'rooms/shared_references'
shared.mkdir(exist_ok=True)
copy(commons_source,shared/'commons_furniture_banners.png')
for f in ['cafe_detail.png','locker_details.png','toilet_details.png']:
    copy(W/'output_v15'/f,shared/f)

equipment_refs=[
    ('bambu_h2d_ams.jpg','Bambu Lab H2D with AMS 2 Pro','The enclosure, dark glazing, toolhead and four-spool AMS 2 Pro appearance only. Exactly TWO installed printer assemblies at the positions in Picture 1. Never substitute Prusa or add printers.'),
    ('formlabs.png','Formlabs resin printer and wash/cure units','Orange translucent resin-printer hood and compact wash/cure equipment appearance only; do not infer an exact product generation or new placement.'),
    ('bigrep.png','BigRep ONE large-format printer','Large square open-frame printer with orange and silver members. Preserve the existing footprint and orientation.'),
    ('wazer.png','WAZER desktop waterjet','White curved side housings, dark front and clear lid, at its existing modeled position.'),
    ('epson.png','Epson garment printer','Dark garment-printer housing, blue detail band and flat garment platen. Keep the modeled footprint.'),
    ('uvflatbed.png','UV flatbed printer appearance guide','Silver and black compact UV flatbed printer with external ink bottles; appearance family guide only, not proof of installed model.'),
    ('spraybooth.jpg','Paasche-style spray booth','Metal benchtop booth, angled side walls and round exhaust duct. Keep it in the modeled corner facing into the room and venting toward the patio; do not relocate it.'),
]

def activity(n):
    if n=='108': return 'Eight fully clothed teenage students and one teacher: three students walk natural short loops along clear bench aisles, four collaborate at existing worktables and one watches a stationary printer. The teacher makes a small gesture. Walking students go around bench ends, never through benches or equipment. Printer housings remain fixed; no moving machine parts or active waterjet/spray operation.'
    if n in ['101','102','105','106']: return 'Ten fully clothed teenage students: four walk in small groups through unobstructed circulation, others sit or talk beside existing furniture. In the cafe two of the walkers approach the existing counter, pause by its TWO iPad POS stands, then walk back. Keep counter equipment, chairs and tables in their reference positions.'
    if n in ['121','122','116','117']: return 'Three fully clothed teenage students walk slowly along the clear entry, locker or washbasin aisles and turn naturally. Others remain outside private compartments. Keep stalls, lockers, benches, basins and showers fixed. No changing, bathing, exposed bodies or activity inside showers or toilet stalls.'
    if n in ['118','119','120','128','109']: return 'Keep this service/storage area quiet and unoccupied. Tiny equipment status-light changes may repeat, but no walking students in restricted plant or storage spaces, no moving machinery and no relocated objects.'
    if n=='GYM': return 'Twelve fully clothed teenage students in athletic clothes: four walk short relaxed loops along clear court-side circulation and the others stand in conversational groups near existing court markings. No running sports play, moving basketballs or changes to floor lines.'
    if n in ['123','130','115','114','110','100']: return 'Four fully clothed teenage students walk naturally in pairs along the clear circulation aisle, gently pass one another with space, turn at clear endpoints and return. One pauses briefly near an existing display or recessed drinking fountain if visible. Keep fountains recessed and preserve every doorway.'
    if n in ['112','113']: return 'Six fully clothed teenage students: two walk around clear table ends and return to their starting points, while four remain seated or compare work at the existing desks. Do not move chairs into the walking path.'
    return 'One fully clothed teenage visitor walks a short unobstructed path from the doorway toward the existing desk, pauses, turns with a natural step and returns. An adult staff member remains seated; if the room is too small for a safe loop, use a brief two-step approach and return. Keep all furniture fixed.'

records=[]
for room in m['rooms']:
    n=room['number']; name=room['name']; D=R/'rooms'/n
    prompt_path=D/'H3_Loop_Prompt.txt'; save_before(prompt_path)
    refs=[{'file':'Topdown_Black.png','title':'Exact overhead layout and room mask','role':'Geometry, framing, scale, positions and black boundary authority.'}]
    photo,caption,exact=cinematic(n)
    refdir=D/'references';refdir.mkdir(exist_ok=True)
    copy(P/'cinematic'/photo,refdir/'02_cinematic.png')
    refs.append({'file':'references/02_cinematic.png','title':'Cinematic appearance guide'+('' if exact else ' (related campus area)'), 'role':'Transfer photographic materials, fully clothed student appearance and fine surface detail only. This eye-level image is NOT a camera, layout, furniture-count or location reference; do not transfer depth of field.'})
    if n=='108':
        for i,(f,title,role) in enumerate(equipment_refs,3):
            dest=f'{i:02d}_{f}';copy(equipment/f,refdir/dest)
            refs.append({'file':'references/'+dest,'title':title,'role':role+' Appearance only; Picture 1 controls scale and placement.'})
    elif n in ['100','101','102','103','104','105','106','110','111','112','113']:
        copy(shared/'commons_furniture_banners.png',refdir/'03_furniture_banners.png')
        refs.append({'file':'references/03_furniture_banners.png','title':'Project render: furniture and King banners','role':'Use the green lounge upholstery, small tables, wood trim and navy/gold King banner appearance only where those objects already exist in Picture 1. Do not import its atrium, camera, floor layout, lighting motion or extra objects.'})
        if n=='101':
            copy(shared/'cafe_detail.png',refdir/'04_cafe_equipment_plan.png')
            refs.append({'file':'references/04_cafe_equipment_plan.png','title':'Cafe equipment detail from source PDF','role':'Read the two POS positions, refrigerated displays, coffee and under-counter equipment as equipment identity/count details. Picture 1 remains the rendered geometry and registration authority. Do not project drawing labels.'})
    elif n in ['121','122','116','117']:
        f='locker_details.png' if n in ['121','122'] else 'toilet_details.png'
        copy(shared/f,refdir/'03_fixture_detail.png')
        refs.append({'file':'references/03_fixture_detail.png','title':'Source plan fixture detail','role':'Fixture and locker configuration detail only. Picture 1 controls exact camera, registration and visible positions. Do not render plan labels or electrical symbols.'})
    elif n in ['123','130','115','114']:
        copy(D/'Room_3D.png',refdir/'03_fixture_shapes.png')
        refs.append({'file':'references/03_fixture_shapes.png','title':'Existing modeled fixture shapes','role':'Supplemental shapes of existing recessed fountains, display cases or doorway trim only. Do not use this cutaway camera or remove walls. Picture 2 guides photographic finish; Picture 1 controls placement.'})

    definitions=[];retention=[]
    for i,ref in enumerate(refs,1):
        definitions.append(f'<Subject {i}>: <Picture {i}> — {ref["title"]}. {ref["role"]}')
        retention.append(f'<Subject {i}>: '+('fully_preserved — exact vertical top-down registration, furniture footprints, doorways and room boundary.' if i==1 else 'attribute_transfer — '+ref['role']))
    prompt='subject_definitions:\n'+'\n'.join(definitions)+f'''\n\nsummary:
[reference generation] A photorealistic 12-second seamless overhead projection loop of {name}, room {n}, with believable campus activity and students walking where appropriate. <Subject 1> alone determines the room location and geometry.

retention_analysis:
'''+ '\n'.join(retention)+f'''

detailed_description:
Locked vertical orthographic architectural photography, square framing, every receiving surface sharply focused. Soft fixed illumination and grounded contact shadows. Fine natural material variation, realistic anatomy and subtle fabric movement. No cinematic lens perspective or depth of field from the appearance references.
[Shot 1] One continuous 12-second shot. {activity(n)} Walkers use natural weight transfer, alternating foot contact, relaxed arm swings and gentle turns at roughly 1.2-1.5 m/s when space permits. Choose short closed paths that fit the actual clear space; never slide, teleport, pass through furniture or cross walls. Stagger starts and maintain personal space. By the loop end return to the opening positions, heading and stride phase smoothly; no abrupt reversal or cut. Seated people make small repeating hand/head gestures. Do not move desks, chairs, equipment, doors or architecture. Preserve every existing object count unless explicitly specified above. No new rooms, roof, walls, objects or decorative text. No camera motion, changing sunlight, moving sun shadows, exposure pumping, flicker or projected light on wall tops. Outside the exact room mask stays pure black. Keep all action inside the mask and reapply the supplied Room_Mask_1024.png after generation for exact registration.

overall_soundscape:
Silent projection output. No dialogue or sound effects.

non_diegetic_music:
None.
'''
    assert len(prompt)<=7000,(n,len(prompt))
    prompt_path.write_text(prompt,encoding='utf-8')
    md=f'# Room {n} — {name}: H3 upload order\n\nUse semantic reference-to-video (local H3-Base-Ref2VA; hosted MiniMax-H3 r2va), **12 seconds**, one fixed overhead shot. Do not use these as first/last-frame endpoints. Upload in this exact order, at most nine images.\n\n'
    for i,ref in enumerate(refs,1): md+=f'{i}. **Picture {i}: [{ref["title"]}]({ref["file"]})** — {ref["role"]}\n\n'
    md+='Then paste [H3_Loop_Prompt.txt](H3_Loop_Prompt.txt). Reapply the room mask after generation. Check walking paths, object counts and the loop seam before projection. References guide generation; they cannot guarantee pixel-exact geometry or a seamless result. No H3 video has been generated.\n'
    (D/'References.md').write_text(md,encoding='utf-8')
    cards=''.join(f'<article><h2>Picture {i}: {html.escape(ref["title"])}</h2><a href="{ref["file"]}" download><img src="{ref["file"]}"></a><p>{html.escape(ref["role"])}</p><a href="{ref["file"]}" download>Download reference {i}</a></article>' for i,ref in enumerate(refs,1))
    (D/'References.html').write_text(f'<!doctype html><meta charset="utf-8"><title>Room {n} H3 references</title><style>body{{background:#101c27;color:#e5f1f3;font:16px system-ui;margin:28px}}a{{color:#8be5cd}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}article{{padding:15px;background:#1b2d39}}img{{width:100%;height:240px;object-fit:contain}}h2{{font-size:18px}}p{{line-height:1.5}}</style><h1>{n} · {html.escape(name)} — {len(refs)} references</h1><p>Upload in numbered order. Picture 1 controls layout; all other images supply only their stated attributes. Fixed top-down, 12 seconds, students walking. <a href="H3_Loop_Prompt.txt">Open prompt</a> · <a href="References.md">Upload instructions</a> · <a href="../">All rooms</a></p><main>{cards}</main>',encoding='utf-8')
    records.append({'room':n,'count':len(refs),'prompt_chars':len(prompt),'references':refs})

(R/'rooms/reference_packs.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(R/'rooms/README.md').write_text('''# Ground-floor H3 room references — r07

Open index.html, select a room's reference pack, upload its images in numbered order, then paste its H3 prompt. Each room has 2–9 image references and a 12-second prompt. The iLab uses all nine slots: overhead, cinematic iLab, Bambu H2D + AMS 2 Pro, Formlabs, BigRep, WAZER, Epson garment printer, UV flatbed printer, spray booth.

Picture 1 is the exact orthographic geometry and mask authority. Photographic and object references control appearance only: never camera, room location, object placement, dimensions or furniture counts. Some cinematic references depict related campus spaces and are explicitly identified. Original architectural render references guide furniture and banner appearance. Fixture-plan excerpts guide equipment identity, not projected drawing labels. Product pictures are existing project references; exact installation variants are not inferred where undocumented. No Prusa reference is included.

Walking is included in circulation and occupied rooms, with fully clothed students, safe clear paths, natural stride and loop closure. Private stalls and showers have no activity; utility/storage rooms stay unoccupied. All shots are fixed top-down, sharply focused, with fixed lighting and black outside the room mask. Reapply Room_Mask_1024.png after generation and review anatomy, collisions, object counts and the seam; H3 does not guarantee precise registration or seamless motion. No H3 videos have been generated.

Topdown_Alpha.png and Topdown_Black.png are 1024-square overhead references. Room_3D.png is a separate Blender cutaway available for inspection; it is NOT displayed on the gym floor. Gym display photographs are in ../projection/cinematic. The original geometric files remain unchanged.
''',encoding='utf-8')

readme=P/'README.md';s=readme.read_text(encoding='utf-8')
s=s.replace('at approximately 1.4 m/s in building scale','at **2× the original speed by default (40 map pixels/second)**; the Walking speed menu offers 1×–4×')
s=s.replace("the room's 1280 x 960 Cycles cutaway",'a cinematic ImageGen photograph')
s+='\n## Cinematic display and H3 references — r07\n\nThe gym uses five ImageGen photographs, including a new wide iLab image. Related-area photographs are shared where a room has no unique cinematic shot; the gym caption explicitly says RELATED VIEW. No gym assignment uses a Blender cutaway. Source provenance is in cinematic/Provenance.md. Room reference packs at ../rooms/index.html list exact H3 upload order, including nine references for the iLab and walking students in fixed overhead loops.\n'
readme.write_text(s,encoding='utf-8')
readme=R/'README.md';s=readme.read_text(encoding='utf-8').replace('**8-second H3 loop prompt**','**12-second H3 loop prompt and a numbered 2–9-image reference pack**').replace('for the interactive display','for inspection; the gym display now uses cinematic ImageGen photographs').replace('all 31 loaded illustrations','all 31 room image assignments')
s+='\n## r07 update\n\nWalking defaults to 2× original speed with a 1×–4× selector. The gym displays five ImageGen photographs; shared related-area images are labeled clearly. Every room has References.html / References.md with H3 upload order and appearance-only roles. The iLab pack uses nine images including two Bambu H2D printers with AMS 2 Pro units. Occupied-room prompts include students walking in clear aisles; service rooms remain unoccupied. Print geometry and source Blender scene were not changed.\n\nFor regeneration, the r07 update script applies after original room/player generation and before package_delivery.py. Do not run it twice on an already updated player; restore its player/index backup first.\n'
readme.write_text(s,encoding='utf-8')

provenance='# Cinematic ImageGen photographs\n\nAll five images are AI-generated appearance guides, not as-built photographs or geometry measurements. Related-room reuse is explicitly captioned.\n\n'
for name,src in photos.items():provenance+=f'- {name}: existing ImageGen output copied unchanged from `{src.relative_to(W)}`.\n'
provenance+='- ilab_wide.png: new built-in ImageGen output. Layout reference: rooms/108/Room_3D.png; product reference: output_v9/equipment/references/bambu_h2d_ams.jpg; appearance reference: guiding_references_v20/02_ilab_03s.png. Two Bambu H2D + AMS 2 Pro assemblies. The photograph remains appearance-only for H3.\n\nProduct references are copied from the existing project equipment reference collection, not newly licensed commercial downloads. Existing source attribution and usage terms continue to apply.\n'
(P/'cinematic/Provenance.md').write_text(provenance,encoding='utf-8')
print('UPDATED',len(records),'room reference packs;',len(photos)+1,'cinematic photographs')
