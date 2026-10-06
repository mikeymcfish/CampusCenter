from production_common import *
import re
ROOT=R/'madmapper_highlight_H04/deliverables';OLD=R/'madmapper_highlight_H03/world_clipped/deliverables';RES=8192;arr=cache_arrays(100,RES);stop=np.asarray(Image.open(H02/'assembly_1_100/Highlight_Stop_IDs_uint8.png'));flat=[]
for y0 in range(0,RES,256):
    sl=np.s_[y0:min(RES,y0+256),:];x=np.asarray(arr['x'][sl],np.float32)/64;y=np.asarray(arr['y'][sl],np.float32)/64
    g=(stop[sl]==13)&(arr['valid'][sl]>0)&(arr['up'][sl]>0)&(arr['z'][sl]<384)&(x>=235)&(x<=448)&(y>=231)&(y<=451);flat.append(np.flatnonzero(g)+y0*RES)
flat=np.concatenate(flat);assert len(flat)==1557104
fire=R/'madmapper_hybrid_UV02/deliverables';fmask=np.asarray(Image.open(fire/'Fireplace_New_Chart_Mask_8192.png'))>0;obj=fire/'CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj';objsha=sha(obj);assert objsha=='b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba'
ap=argparse.ArgumentParser();ap.add_argument('--sids',nargs='+',type=int,required=True);args=ap.parse_args();rows=[];review=ROOT/'Review_Sheets';review.mkdir(exist_ok=True)
oldreviews=json.loads((OLD/'Review_Sheets/Review_Sheets_Manifest.json').read_text());cfg=config(100);W,H=cfg['top_size'];cx,cy=cfg['center'];cw,ch=cfg['canvas']
def worldbox(bounds,pad=2):
    (x0,y0),(x1,y1)=bounds
    return (max(0,int((x0-cx+cw/2)/cw*W)-pad),max(0,int((cy+ch/2-y1)/ch*H)-pad),min(W,int((x1-cx+cw/2)/cw*W)+pad+1),min(H,int((cy+ch/2-y0)/ch*H)+pad+1))
fbox=worldbox([[514,317],[548,338]],4)
for sid in args.sids:
    title,body=COPY['spaces'][sid-1];slug=re.sub(r'[^A-Za-z0-9]+','_',title).strip('_');folder=ROOT/slug;origin=OLD/slug;q=json.loads((folder/'Pagination_QA.json').read_text());oq=json.loads((origin/'Pagination_QA.json').read_text());native=json.loads((folder/'Native_Hybrid_Media_Reapplication_QA.json').read_text());clip=json.loads((folder/'Compact_Mapped_Preview_QA.json').read_text());mapping=json.loads((folder/'Room_Highlight_World_Mapping_QA.json').read_text())
    assert native['status']=='PASS' and native['receiver_OBJ_sha256']==objsha and all(x['identity_world_transform'] for x in native['import_checks']);assert clip['all_preview_frames_decoded'];assert mapping['status']=='PASS'
    assert q['page_count']==oq['page_count'] and q['official_title_exact']==title and q['official_body_exact']==body and not q['presentation_room_number_labels'];assert q['caption_bounds_model_mm']==[[235,231],[448,451]]
    assert q['highlight_mask_sha256']==sha(OLD/q['highlight_mask']);assert ' '.join(' '.join(e['lines']) for e in q['pages'])==re.sub(r'\s+',' ',body).strip()
    assert q['colour_and_fixture_shading_QA']['same_hue_max_RGB_byte_residual']<=1.01 and q['floor_linear_colour_factor_ratio_vs_H03_median']>1
    pagechecks=[];images=[]
    for oldentry,entry in zip(oq['pages'],q['pages']):
        original=origin/oldentry['atlas'];atlasfile=folder/entry['atlas'];assert sha(original)==oldentry['atlas_sha256']==entry['source_H03_page_sha256'];assert entry['lines']==oldentry['lines'];assert sha(atlasfile)==entry['atlas_sha256'];assert any(x['atlas_sha256']==entry['atlas_sha256'] for x in native['renders'])
        atlas=np.asarray(Image.open(atlasfile).convert('RGB'));older=np.asarray(Image.open(original).convert('RGB'));assert np.array_equal(atlas.reshape(-1,3)[flat],older.reshape(-1,3)[flat]);on=int(np.any(atlas[fmask],axis=1).sum());assert bool(on)==(sid==3)
        path=folder/(atlasfile.stem.replace('_Atlas_8192','')+'_Native_Mapped_Preview.png');images.append(Image.open(path).convert('RGB'))
        pagechecks.append({'page':entry['page'],'atlas':entry['atlas'],'sha256':entry['atlas_sha256'],'caption_matches_final_H03_texels':True,'official_lines_unchanged':True,'native_render_matches_current_atlas_hash':True,'fireplace_nonzero_chart_texels':on,'fireplace_on':sid==3})
    inherited=oldreviews['reviews'][sid-1];roomcrop=inherited['room_crop_native_box'];captioncrop=inherited['caption_crop_native_box'];room=images[0].crop(roomcrop);captioncrops=[im.crop(captioncrop) for im in images]
    width=max(sum(c.width for c in captioncrops)+12*(len(images)-1),room.width);sheet=Image.new('RGB',(width,captioncrops[0].height+room.height+65),(10,17,25));dr=ImageDraw.Draw(sheet);dr.text((10,8),title+' | H04 brighter room, same-hue dim furniture',font=ImageFont.truetype(str(FONT),20),fill='white');pos=0
    for crop in captioncrops:sheet.paste(crop,(pos,35));pos+=crop.width+12
    sheet.paste(room,(0,captioncrops[0].height+50));sheet.save(review/(slug+'_Combined_Caption_And_Room_Review.png'))
    firecrop=images[0].crop(fbox);firecrop.save(review/(slug+'_Fireplace_Actual_Native_Crop.png'))
    oldnative=Image.open(origin/(q['pages'][0]['atlas'].replace('_Atlas_8192.png','_Native_Mapped_Preview.png'))).convert('RGB');left=oldnative.crop(roomcrop);comparison=Image.new('RGB',(room.width*2+12,room.height+35),(10,17,25));comparison.paste(left,(0,35));comparison.paste(room,(room.width+12,35));d=ImageDraw.Draw(comparison);d.text((8,8),'H03',font=ImageFont.truetype(str(FONT),18),fill='white');d.text((room.width+20,8),'H04',font=ImageFont.truetype(str(FONT),18),fill='white');comparison.save(review/(slug+'_H03_H04_Room_Comparison.png'))
    q['native_preview_pending']=False;q['status']='PASS: media, caption, unchanged receiver/masks, native reapplication and full clip decode verified; visual review pending';q['visual_review_complete']=False;(folder/'Pagination_QA.json').write_text(json.dumps(q,indent=2))
    rows.append({'sid':sid,'title':title,'pages':pagechecks,'colour_RGB':q['colour_RGB'],'fixture_colour_QA':q['colour_and_fixture_shading_QA'],'floor_colour_ratio_vs_H03':q['floor_linear_colour_factor_ratio_vs_H03_median'],'clip_path':clip['file'],'clip_sha256':clip['sha256'],'clip_bytes':clip['bytes'],'clip_seconds':clip['duration_seconds'],'review_sheet':str(review/(slug+'_Combined_Caption_And_Room_Review.png')),'room_comparison':str(review/(slug+'_H03_H04_Room_Comparison.png')),'fireplace_crop':str(review/(slug+'_Fireplace_Actual_Native_Crop.png')),'inherited_world_mask_mapping_QA':mapping['status'],'original_H03_pages_hash_verified_unchanged':True});print('H04 FULL ATLAS/NATIVE/WORDS/COLOUR/FIREPLACE AUDIT PASS',title,flush=True)
p=ROOT/'H04_All_Stop_Media_QA.json';prev=json.loads(p.read_text()) if p.exists() else {};merged={x['sid']:x for x in prev.get('rows',[])};merged.update({x['sid']:x for x in rows})
qa={'status':'PASS: audited derived media; visual review pending','stops_audited':len(merged),'pages_audited':sum(len(x['pages']) for x in merged.values()),'receiver_OBJ_sha256':objsha,'geometry_UVs_shared_origin_scale_changed':False,'H03_alpha_masks_byte_identical_reused':True,'gym_caption_pixels_and_balanced_pagination_match_H03':True,'displayed_room_numbers':False,'fireplace_only_Commons':True,'all_selected_fixture_surfaces_same_hue_dimmer':True,'fixture_normal_height_contact_depth_shading_retained':True,'native_shader':'Emission1; no scene lights; actual UV02 all4parts; nearest texture','physical_projection_or_MadMapper_playback_verified':False,'rows':[merged[k] for k in sorted(merged)]};p.write_text(json.dumps(qa,indent=2))
