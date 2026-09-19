from pathlib import Path
import json,sys,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).parent;rooms=json.loads((R/'rooms/room_contract.json').read_text())
pilot='--pilot' in sys.argv
actions={
 '108':'Four fully clothed teenage students work at the existing central benches: two compare a small prototype, one sketches, and one studies a stationary 3D printer. A teacher leans in briefly. Small hand and head gestures return to their starting positions; no one crosses a wall or moves the equipment.',
 '102':'Small groups of fully clothed teenage students sit in the existing chairs and sofas, chat quietly, turn a page, and exchange a relaxed glance. Two students near the clear circulation route pause in conversation. Keep every table and seat exactly where shown.',
 '101':'One adult cafe attendant behind the existing counter taps one of the existing POS tablets. Two fully clothed students wait on the customer side, nod and adjust their hands. Keep the food-service equipment, counter and queue within the pictured footprint.',
 'GYM':'Six fully clothed teenage students practice gentle ball passing within the existing gym floor. One controlled pass travels between two stationary students and returns. Other students shift their weight. Keep the room outline and floor finish fixed; do not invent court markings or equipment absent from the reference.',
 '105':'Three fully clothed teenage students quietly examine student work along the gallery. One points briefly and lowers their hand; another tilts their head and returns. Keep all display objects and circulation clear.',
 '103':'An adult receptionist sits at the existing desk and looks up to greet a fully clothed visitor. A small nod and hand gesture settle back to the initial pose. No furniture changes.',
 '104':'Two adults seated at the existing admissions furniture review a document with subtle hand movements and return their attention to the starting position.',
 '129':'An adult athletic trainer and a fully clothed student discuss a clipboard beside the existing treatment furniture. Gentle conversational gestures only; no treatment or injury depiction.',
 '113':'Four fully clothed teenage students collaborate around the existing furniture, pointing at notebooks and exchanging glances before returning to their initial positions.',
 '112':'A small group of fully clothed teenage students uses the existing classroom desks. One adult teacher gestures toward a page, then relaxes. Keep the arrangement exactly as pictured.',
}
def action(r):
 n=r['number'];name=r['name'].lower()
 if n in actions:return actions[n]
 if n in ['116','117']:return 'The restroom is empty. Preserve toilets, partitions, basins and entrances exactly; a restrained reflection shimmer on existing metal fixtures is the only motion. No people, added fixtures, or running taps.'
 if n in ['121','122']:return 'The locker and shower room is empty. Preserve benches, lockers, shower partitions and all fixtures exactly. A barely perceptible reflection on existing fixtures settles back to its start. No people or changing activity.'
 if any(w in name for w in ['storage','mech','janitor']):return 'The utility or storage room remains empty and orderly. Retain every pictured shelf, cabinet and service fixture. Only a very subtle stable reflection shimmer is permitted; do not invent equipment, people or operating machinery.'
 if 'office' in name:return 'One adult sits at the existing desk, briefly turns a page and returns their hands to their initial position. A quiet, natural office moment. Keep the desk, seating and circulation exactly as pictured.'
 return 'Two fully clothed teenage students stand to one side of the existing clear circulation route, quietly exchange a glance and a small gesture, then return to their initial poses. Keep doorways clear and all display furniture fixed.'
report=[];thumbs=[]
for r in rooms:
 d=R/'rooms'/r['number'];raw=d/('topdown_pilot_raw.png' if pilot else 'topdown_raw.png')
 if not raw.exists():continue
 x0,y0,x1,y1=r['mask_bounds_px'];side=max(x1-x0,y1-y0)+16;cx=(x0+x1)/2;cy=(y0+y1)/2
 full=Image.open(d/'mask_full_canvas.png').convert('L')
 mask=full.transform((1024,1024),Image.Transform.EXTENT,(cx-side/2,cy-side/2,cx+side/2,cy+side/2),Image.Resampling.NEAREST)
 im=Image.open(raw).convert('RGB');rgba=im.convert('RGBA');rgba.putalpha(mask)
 black=Image.new('RGB',im.size);black.paste(im,(0,0),mask)
 suffix='_pilot' if pilot else ''
 rgba.save(d/f'Topdown_Alpha{suffix}.png');black.save(d/f'Topdown_Black{suffix}.png');mask.save(d/'Room_Mask_1024.png')
 assert np.array(black)[np.array(mask)==0].max()==0
 if not pilot:
  prompt=f'''subject_definitions:\n<Subject 1>: <Picture 1> is the exact orthographic ground-floor layout of {r['name'].title()}, room {r['number']}, in the King School Campus Center. Preserve its room shape, camera orientation, openings, floor pattern, furniture footprints and all visible equipment. The black area is outside the room and must remain pure black.\n\nsummary:\n[reference generation] A refined, photorealistic eight-second overhead architectural scene of <Subject 1>, with restrained believable activity and a calm repeating rhythm.\n\nretention_analysis:\nRetain the exact vertical top-down camera, square crop, scale, floor boundary and every pictured architectural feature. No camera motion, perspective tilt, depth of field, zoom, wall growth, furniture rearrangement or changing shadows. Improve material realism, fabric, paint and fine surface detail without replacing equipment or changing geometry. Do not extend the scene beyond the room mask.\n\ndetailed_description:\nA completely locked orthographic view looking straight down, everything sharply focused from corner to corner. Soft, fixed architectural illumination; natural colors and realistic fine textures. {action(r)} Throughout 0-8 seconds, motions are small, smooth and cyclic; each visible person or object returns to the initial pose or state at the end. No entrances or exits across the crop, no flicker, moving sunlight, dramatic effects, titles or logos. Photographic material response, anatomically coherent people where specified, grounded contact shadows, quiet school atmosphere.\n\noverall_soundscape:\nSilent output for projection mapping; no dialogue or generated sound is needed.\n\nnon_diegetic_music:\nNone.\n'''
  (d/'H3_Loop_Prompt.txt').write_text(prompt,encoding='utf-8')
 thumb=black.copy();thumb.thumbnail((250,250));tile=Image.new('RGB',(280,300),'#101922');tile.paste(thumb,((280-thumb.width)//2,10));dr=ImageDraw.Draw(tile);ff=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13);dr.text((10,265),r['number']+'  '+r['name'],font=ff,fill='white');thumbs.append(tile)
 report.append({'room':r['number'],'alpha_bounds':rgba.getbbox(),'blackout_pass':True,'mask_pixels':int((np.array(mask)>0).sum())})
sheet=Image.new('RGB',(280*6,300*math.ceil(len(thumbs)/6)),'#080d13')
for i,im in enumerate(thumbs):sheet.paste(im,(i%6*280,i//6*300))
sheet.save(R/'rooms'/('Pilot_Contact_Sheet.jpg' if pilot else 'Room_Contact_Sheet.jpg'))
(R/'rooms'/('pilot_mask_validation.json' if pilot else 'mask_validation.json')).write_text(json.dumps(report,indent=2))
if not pilot:
 assert len(report)==31,len(report)
 (R/'rooms/README.md').write_text('''# Ground-floor room reference pack\n\n31 named rooms and circulation/display areas, each with a 1024-square vertical orthographic render. No perspective or depth of field. `Topdown_Alpha.png` isolates the room; `Topdown_Black.png` is the black-matted H3 reference; `Room_Mask_1024.png` is the exact final compositing mask. `mask_full_canvas.png` places the room on the 2048 x 1572 projection canvas.\n\nThe layout is the existing furnished Blender model, not an architect-verified as-built. Open commons/cafe/gallery/reception areas have display boundaries rather than invented walls. The mask-area values are diagnostic and are not a room-area schedule.\n\n## H3\nAttach the room's `Topdown_Black.png` as Picture 1, paste `H3_Loop_Prompt.txt`, choose reference-image video (local H3-Base-Ref2VA / hosted r2va, MiniMax-H3), 8 seconds, square format. Prompts follow the manual six-section reference-generation format. No videos have been generated by H3.\n\nA prompt cannot guarantee a seamless loop, accurate anatomy or perfect geometry. Review the result; trim to matching phases or blend a short overlap. For a stricter endpoint workflow, first approve one photorealistic still, then use that SAME image as first and last frame in the separate first/last-frame mode. Do not confuse semantic reference mode with exact endpoints.\n\nAlways reapply the supplied mask AFTER video generation. Resize into the square world extent in room_contract.json, then composite onto the full canvas and multiply by the print receiver mask. This prevents AI spill onto walls and adjacent rooms. Keep the video camera and sunlight fixed.\n\nRoom images are deliberately empty of temporary mannequins. Prompts specify restrained appropriate activity; locker rooms and bathrooms remain empty. `Room_3D.png`, when present, is an additional oblique cutaway illustration used by the exploration player and is NOT a projection registration reference.\n''',encoding='utf-8')
print('FINISHED',len(report),flush=True)
