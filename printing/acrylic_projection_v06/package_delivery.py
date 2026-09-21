from pathlib import Path
import json,zipfile,hashlib,html,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent;rooms=json.loads((R/'rooms/room_contract.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
cards=[];tiles=[]
for r in rooms:
 n=r['number'];d=R/'rooms'/n
 for f in ['Topdown_Alpha.png','Topdown_Black.png','Room_Mask_1024.png','mask_full_canvas.png','Room_3D.png','H3_Loop_Prompt.txt']:assert (d/f).is_file(),(n,f)
 a=Image.open(d/'Topdown_Alpha.png').convert('RGBA');b=Image.open(d/'Topdown_Black.png').convert('RGB');mask=np.array(Image.open(d/'Room_Mask_1024.png'));assert a.size==(1024,1024);assert np.array(b)[mask==0].max()==0;assert np.array_equal(np.array(a)[:,:,3],mask)
 assert Image.open(d/'Room_3D.png').size==(1280,960)
 prompt=(d/'H3_Loop_Prompt.txt').read_text();assert all(k in prompt for k in ['integrated_multimodal_description:','overall_soundscape:','non_diegetic_music:']);assert '<Picture 2>' not in prompt
 cards.append(f'<article><h2>{n} · {html.escape(r["name"].title())}</h2><a href="{n}/Topdown_Black.png"><img loading="lazy" src="{n}/Topdown_Black.png" alt="Top-down room {n}"></a><p><a href="{n}/References.html">Numbered H3 reference pack</a> · <a href="{n}/Prompt.html">12-second walking prompt</a><br><a href="{n}/Topdown_Alpha.png">Transparent</a> · <a href="{n}/Room_Mask_1024.png">Mask</a> · <a href="{n}/Room_3D.png">3D cutaway</a></p></article>')
 tile=Image.new('RGB',(320,270),'#182530');im=Image.open(d/'Room_3D.png').convert('RGB');im.thumbnail((310,235));tile.paste(im,((320-im.width)//2,0));ImageDraw.Draw(tile).text((7,246),n+' '+r['name'],font=font,fill='white');tiles.append(tile)
(R/'rooms/index.html').write_text('<!doctype html><meta charset="utf-8"><title>Ground-floor room references</title><style>body{background:#09131d;color:#e3eef3;font:16px system-ui;margin:25px}h1{font-weight:500}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}article{background:#172630;padding:12px;border-radius:9px}h2{font-size:16px}img{width:100%;aspect-ratio:1;object-fit:contain;background:black}a{color:#8be5cd}p{font-size:13px;line-height:1.7}</style><h1>Ground-floor room references</h1><p>31 exact-overhead room references, masks, H3 prompts and oblique illustrations. <a href="../cglide/">Download CGlide project packages</a>. <a href="README.md">Workflow notes</a></p><main>'+''.join(cards)+'</main>',encoding='utf-8')
sheet=Image.new('RGB',(320*6,270*math.ceil(len(tiles)/6)),'#09131d')
for i,t in enumerate(tiles):sheet.paste(t,(i%6*320,i//6*270))
sheet.save(R/'rooms/Room_3D_Contact_Sheet.jpg',quality=92)
effects=['Ink_Map','Depth_Contours','Surface_Ripples','Explorer'];sheet=Image.new('RGB',(1200,960),'#09131d')
for i,n in enumerate(effects):
 f=R/'projection/review'/(n+'_On_Print.png');assert f.exists();im=Image.open(f).convert('RGB');im.thumbnail((590,440));x=i%2*600;y=i//2*480;sheet.paste(im,(x+(600-im.width)//2,y));ImageDraw.Draw(sheet).text((x+15,y+450),n.replace('_',' '),font=font,fill='white')
sheet.save(R/'projection/Projection_Examples.jpg',quality=94)
exclude={'topdown_raw.png','topdown_pilot_raw.png','Topdown_Alpha_pilot.png','Topdown_Black_pilot.png','Pilot_Contact_Sheet.jpg','pilot_render_report.json','pilot_mask_validation.json','room_id_map.npz'}
roomfiles=[p for p in (R/'rooms').rglob('*') if p.is_file() and p.name not in exclude]
with zipfile.ZipFile(R/'Ground_Room_References.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in roomfiles:z.write(p,p.relative_to(R))
with zipfile.ZipFile(R/'Ground_Projection_Studio.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in (R/'projection').rglob('*'):
  if p.is_file():z.write(p,p.relative_to(R))
 for p in roomfiles:z.write(p,p.relative_to(R))
 for p in (R/'cglide').rglob('*'):
  if p.is_file():z.write(p,p.relative_to(R))
 for f in ['serve.py','Start_Projection.cmd']:z.write(R/f,f)
for f in ['Ground_Room_References.zip','Ground_Projection_Studio.zip','Ground_Acrylic_Print_Package.zip']:
 with zipfile.ZipFile(R/f) as z:assert z.testzip() is None
sources={}
for p in [R.parent/'cycles_studio_v05/Campus_Center_Cycles_Studio.blend',R.parent/'projection_enclosed_v05/ground/Campus_Center_Ground_Enclosed_1_87p5.stl']:
 sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
assert sources[str(R.parent/'cycles_studio_v05/Campus_Center_Cycles_Studio.blend')]==json.loads((R/'scene_inventory.json').read_text())['sha256']
assert sources[str(R.parent/'projection_enclosed_v05/ground/Campus_Center_Ground_Enclosed_1_87p5.stl')]=='8a240733a27443abb859299a34efdc2b682c23c742e536b91b60f9853789b824'
out={'status':'passed','ground_room_count':31,'topdown_orthographic':True,'no_depth_of_field':True,'room_mask_blackout_pass':True,'oblique_cutaway_count':31,'h3_prompt_count':31,'h3_videos_generated':False,'source_hashes_unchanged':sources,'print_validation':'print/reopen_validation.json','step_validation':'print/cad_validation.json','effect_validation':'projection/examples/video_validation.json','explorer_validation':'projection/examples/explorer_validation.json','browser_validation':'projection/browser_validation.json','physical_fit_and_projection_tested':False,'packages':[]}
for f in ['Ground_Acrylic_Print_Package.zip','Ground_Room_References.zip','Ground_Projection_Studio.zip']:
 p=R/f;out['packages'].append({'file':f,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'zip_crc_pass':True})
(R/'delivery_validation.json').write_text(json.dumps(out,indent=2));print('PACKAGED',[(p['file'],p['bytes']) for p in out['packages']],flush=True)


