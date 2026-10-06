from production_common import *
from hybrid_projection_cache import load
import re,copy

ap=argparse.ArgumentParser();ap.add_argument('--sids',nargs='+',type=int,required=True);args=ap.parse_args()
OLD=R/'madmapper_highlight_H03/world_clipped/deliverables';ROOT=R/'madmapper_highlight_H04/deliverables';ROOT.mkdir(parents=True,exist_ok=True);RES=8192
source_obj=config(100)['obj'];v,u,n,parts=parse_obj(source_obj);p=parts['Opaque'];centers,norm,area=geom(v,p['f'])
surfaces=json.loads((config(100)['source']/'Surface_Lookup_Manifest.json').read_text())['surfaces']
manifest=json.loads((OLD/'World_Clipped_Mask_Manifest.json').read_text());palette=json.loads((H02/'assembly_1_100/Stop_Selection_Manifest.json').read_text())['color_palette_RGB']
arr=cache_arrays(100,RES);cfg=config(100);top=load();height=top['height'];HH,WW=height.shape
near=np.asarray(Image.fromarray(np.uint8(height>6)*255).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(5)),np.float32)/255
ld=np.array([-.38,.50,.78]);ld/=np.linalg.norm(ld);stop=np.asarray(Image.open(H02/'assembly_1_100/Highlight_Stop_IDs_uint8.png'))
gym=np.zeros((RES,RES),bool);caption=np.zeros_like(gym)
for y0 in range(0,RES,256):
    sl=np.s_[y0:min(RES,y0+256),:];xx=arr['x'][sl]/64.;yy=arr['y'][sl]/64.
    g=(stop[sl]==13)&(arr['valid'][sl]>0)&(arr['up'][sl]>0)&(arr['z'][sl]<6*64)
    gym[sl]=g;caption[sl]=g&(xx>=235)&(xx<=448)&(yy>=231)&(yy<=451)
assert caption.sum()==1557104
fire=R/'madmapper_hybrid_UV02/deliverables';obj=fire/'CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj';objsha=sha(obj);assert objsha=='b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba'
fmask=np.asarray(Image.open(fire/'Fireplace_New_Chart_Mask_8192.png'))>0;fpatch=np.asarray(Image.open(fire/'Fireplace_Only_Patch_8192.png').convert('RGB'))
fm=json.loads((fire/'UV02_Compatibility_And_Surface_Manifest.json').read_text());fv,fu,fn,fp=parse_obj(obj);firepart=fp['Opaque_Fireplace_P03_B3'];_,fire_normal,fire_area=geom(fv,firepart['f']);assert len(fm['new_surfaces'])==len(firepart['f'])==2756
cause=[]
for sid in args.sids:
    title,body=COPY['spaces'][sid-1];slug=re.sub(r'[^A-Za-z0-9]+','_',title).strip('_');origin=OLD/slug;q=json.loads((origin/'Pagination_QA.json').read_text());folder=ROOT/slug;folder.mkdir(exist_ok=True);assert not (folder/'Pagination_QA.json').exists()
    assert q['official_title_exact']==title and q['official_body_exact']==body and ' '.join(' '.join(e['lines']) for e in q['pages'])==re.sub(r'\s+',' ',body).strip()
    alpha=np.asarray(Image.open(OLD/q['highlight_mask']),np.float32)/255;prior=np.array([72,201,182] if sid==3 else palette[sid],np.float32);colour=np.rint(prior/prior.max()*255).astype(np.float32)
    base=np.zeros((RES,RES,3),np.uint8);counts={'receiver_charts':0,'selected_receiver_texels':0,'raised_fixture_or_wall_texels':0,'same_hue_max_RGB_byte_residual':0.};floor_ratios=[]
    for s in surfaces:
        if s['geometry_part']!='Opaque' or s['surface_role']=='Underside':continue
        x,y,w,h=s['uv_pixel_rectangle_bottom_up'];x0=int(x);x1=int(x+w);y0=int(RES-y-h);y1=int(RES-y);sl=np.s_[y0:y1,x0:x1];a=alpha[sl]
        if not np.any(a):continue
        indices=np.array(s['source_face_indices_0based']);fi=indices[np.argmax(area[indices])];t=v[p['f'][fi]];ut=u[p['ft'][fi]]*np.array([RES,-RES])+[0,RES]
        affine=np.linalg.solve(ut[1:]-ut[0],t[1:]-t[0]);py,px=np.mgrid[y0:y1,x0:x1];xyz=np.stack([px+.5-ut[0,0],py+.5-ut[0,1]],axis=2)@affine+t[0];valid=arr['valid'][sl]>0
        for k,axis in [('x',0),('y',1),('z',2)]:xyz[:,:,axis]=np.where(valid,arr[k][sl]/64.,xyz[:,:,axis])
        up=np.where(valid,arr['up'][sl]>0,norm[fi,2]>.9);oldlight=np.where(valid,arr['light'][sl]/255.,(.4+.6*max(0,float(norm[fi]@ld))))
        tx=np.clip(np.floor((xyz[:,:,0]-cfg['center'][0]+cfg['canvas'][0]/2)/cfg['canvas'][0]*WW).astype(int),0,WW-1);ty=np.clip(np.floor((cfg['center'][1]+cfg['canvas'][1]/2-xyz[:,:,1])/cfg['canvas'][1]*HH).astype(int),0,HH-1)
        z=xyz[:,:,2];shade=(.68+.32*np.clip((oldlight-.4)/.6,0,1))*(1-.12*near[ty,tx])*(1-.06*np.clip(z/47,0,1))
        raised=z>=5.8;dimmer=np.where(up,np.where(raised,.72,1.),.48);factor=shade*dimmer*a
        rgb=np.uint8(np.clip(np.rint(colour*factor[:,:,None]),0,255));base[sl]=rgb
        active=a>0;dominant=int(np.argmax(colour));residual=abs(rgb.astype(float)-rgb[:,:,dominant,None]/255*colour)
        counts['same_hue_max_RGB_byte_residual']=max(counts['same_hue_max_RGB_byte_residual'],float(residual[active].max()));counts['receiver_charts']+=1;counts['selected_receiver_texels']+=int(active.sum());counts['raised_fixture_or_wall_texels']+=int((active&raised).sum())
        floor=active&up&~raised&valid
        if floor.any():floor_ratios.extend((shade[floor]/np.maximum(oldlight[floor]*(1-.23*near[ty,tx][floor])*(1-.10*np.clip(z[floor]/47,0,1)),1e-6)*(colour.max()/prior.max())).tolist())
    assert counts['same_hue_max_RGB_byte_residual']<=1.01,counts
    if sid==3:
        for s in fm['new_surfaces']:
            fi=s['new_part_face_index_0based'];x0,y0,w,h=s['rectangle_top_down_px'];sl=np.s_[y0:y0+h,x0:x0+w];a=fmask[sl];t=fv[firepart['f'][fi]];ut=fu[firepart['ft'][fi]]*np.array([RES,-RES])+[0,RES]
            affine=np.linalg.solve(ut[1:]-ut[0],t[1:]-t[0]);py,px=np.mgrid[y0:y0+h,x0:x0+w];xyz=np.stack([px+.5-ut[0,0],py+.5-ut[0,1]],axis=2)@affine+t[0]
            nn=fire_normal[fi];shade=(.68+.32*max(0,float(nn@ld)))*(1-.06*np.clip(xyz[:,:,2]/47,0,1));dimmer=.72 if nn[2]>.9 else (.35 if nn[2]<-.9 else .48)
            rgb=np.uint8(np.clip(np.rint(colour*shade[:,:,None]*dimmer),0,255));base[sl][a]=rgb[a]
        assert np.any(base[fmask])
    else:assert not np.any(base[fmask])
    records=[];cause_pages=[]
    for entry in q['pages']:
        src=origin/entry['atlas'];original=np.asarray(Image.open(src).convert('RGB'));assert np.array_equal(original[fmask],fpatch[fmask]);atlas=base.copy();preserve=caption if sid==13 else gym;atlas[preserve]=original[preserve]
        assert np.array_equal(atlas[caption],original[caption]);assert np.array_equal(atlas[fmask],base[fmask]);png=folder/entry['atlas'];Image.fromarray(atlas).save(png)
        e=copy.deepcopy(entry);e.update({'atlas_sha256':sha(png),'source_H03_page':str(src),'source_H03_page_sha256':sha(src),'caption_pixels_exactly_preserved':True,'fireplace_patch_exactly_preserved':False,'fireplace_selected_only_in_Commons':True});records.append(e);cause_pages.append({'page':entry['page'],'old_neutral_fireplace_chart_pixels_exact':True,'old_fireplace_nonzero_texels':int(np.any(original[fmask],axis=1).sum()),'new_fireplace_nonzero_texels':int(np.any(atlas[fmask],axis=1).sum())})
        print('H04 BRIGHT SAME-HUE PAGINATED ATLAS READY',slug,entry['page'],flush=True)
    q.update({'status':'PASS: brighter same-hue receiver and Commons-only fireplace; native and viewing validation pending','pages':records,'revision':'H04: media only; H03 retained','source_H03_pagination_QA':str(origin/'Pagination_QA.json'),'colour_RGB':colour.astype(int).tolist(),'previous_H03_colour_RGB':prior.astype(int).tolist(),'colour_and_fixture_shading_QA':counts,'floor_linear_colour_factor_ratio_vs_H03_median':float(np.median(floor_ratios)) if floor_ratios else None,'fixture_colour':'All selected non-underside opaque surfaces use room hue; raised surfaces atz>=5.8mm use0.72 top multiplier,0.48 side multiplier. Normal,height and contact shading preserved; no neutral furniture replacements. Raised-wall surfaces share this treatment.','fireplace_control':'Dedicated UV02 fireplace charts use Commons hue and dim fixture shading only during Commons; RGB0 on every other stop. No neutral compatibility patch added.','restored_fireplace_patch_exactly_matches_hybrid_UV02':False,'all_caption_pixels_exactly_preserved_from_final_H03':True,'geometry_UV_origin_or_scale_changed':False,'native_preview_pending':True,'room_highlight_mapping_validation_pending':False,'visual_review_complete':False,'physical_projector_readability_verified':False})
    for e in q['pages']:assert e['lines']==json.loads((origin/'Pagination_QA.json').read_text())['pages'][e['page']-1]['lines']
    (folder/'Pagination_QA.json').write_text(json.dumps(q,indent=2));cause.append({'stop':title,'sid':sid,'fireplace_chart_count':2756,'new_same_hue_RGB':colour.astype(int).tolist(),'fixture_QA':counts,'floor_colour_ratio_median':q['floor_linear_colour_factor_ratio_vs_H03_median'],'pages':cause_pages})
    for name in ['Room_Highlight_World_Mapping_QA.json']:
        inherited=json.loads((origin/name).read_text());inherited['H04_status']='Inherited exact H03 masks and receiver unchanged; appendix fireplace is explicitly Commons only';(folder/name).write_text(json.dumps(inherited,indent=2))
    print('H04 STOP COMPLETE',slug,json.dumps(counts),flush=True)
previous=ROOT/'Fireplace_And_Furniture_Colour_Cause_QA.json';prev=json.loads(previous.read_text()) if previous.exists() else {}
rows={x['sid']:x for x in prev.get('rows',[])};rows.update({x['sid']:x for x in cause})
audit={'status':'PASS: observed H03 causes confirmed in actual charts and page pixels; H04 media revision removes both','fireplace_UV_mapped':True,'receiver_part':'Opaque_Fireplace_P03_B3','appended_charts':2756,'fireplace_bounds_model_mm':fm['new_closed_fireplace']['bounds_mm'],'receiver_OBJ_sha256':objsha,'H03_cause':'highlight_h03_world_caption_media.py assigns base[firemask]=firepatch[firemask] for every sid; all inspected H03 page pixels exactly match the neutral UV02 patch. Fresh native preview uses one Emission atlas on all4parts, no scene lights; persistent fireplace light originates in atlas, not additional scene lighting.','furniture_cause':'H03 replaces upward surfacesz5.8..22 with[228,230,221] andz>=22 with[139,174,182], overriding selected room hue.','H04_solution':'Room palette rescaled to maximum255; gentler normal/contact/height shading; all raised surfaces have dim same-hue top/side values; fireplace charts illuminated only for Commons.','geometry_UV_scale_origin_changes':False,'all_H03_history_preserved':True,'physical_projection_or_MadMapper_playback_verified':False,'rows':[rows[k] for k in sorted(rows)]}
previous.write_text(json.dumps(audit,indent=2));print('H04 CAUSE AND BUILD QA WRITTEN',flush=True)
