from pathlib import Path
import json,numpy as np
import ripple_r04_thin_ridge_transfer as transfer
R=Path(__file__).parent;T=R/'madmapper_ripple_R04/whole_model';D=T/'deliverables';qa=json.loads((T/'Staggered_Connected_Wave_Physics_QA.json').read_text())
row=next(q for q in qa['components'] if any(e['reference_owner']==999 for e in q['source_events']));event=next(e for e in row['source_events'] if e['reference_owner']==999);q=next(c for c in transfer.components if c['name']==row['name'])
npz=np.load(R/'madmapper_ripple_R03/whole_model'/(row['name']+'_Simulation_Domain.npz'));origin=npz['origin'];source=np.array(event['point_model_mm']);iy=int(np.floor((source[1]-origin[1])/.5));frame=60;field=q['fields'][frame];intensity=transfer.ridge(q,frame)
gridx=origin[0]+(np.arange(field.shape[1])+.5)*.5;radius=np.arange(25.,85.,.025);xx=source[0]+radius;h=np.interp(xx,gridx,field[iy]);thin=np.interp(xx,gridx,intensity[iy]);legacy=-np.expm1(-(np.maximum(h,0)*1200.)**2)
peak=int(np.argmax(h));target=radius[peak]
def fwhm(values):
    close=np.flatnonzero(abs(radius-target)<3);i=close[np.argmax(values[close])];half=values[i]*.5;left=i;right=i
    while left>0 and values[left-1]>=half:left-=1
    while right<len(values)-1 and values[right+1]>=half:right+=1
    return float(radius[right]-radius[left]),float(values[i]),float(radius[i])
nw,npeak,nradius=fwhm(thin);ow,opeak,oradius=fwhm(legacy);assert nw>0 and ow>0 and nw<ow*.4,(nw,ow)
result={'status':'PASS: actual isolated Gym crest substantially thinner than R03 transfer on same solved field','actual_R04_field_component':q['name'],'actual_frame':frame,'time_seconds':3,'source_time_seconds':event['time_seconds'],'source_point_model_mm':source.tolist(),'measurement':'Horizontal outward ray on actual unobstructed Gym floor through the isolated solved wave. R04 samples the actual ridge-intensity grid bilinearly. R03 comparison evaluates its1-exp(-(positive_height*1200)^2) crest response on this same actual height field; quiet ambient wash excluded. FWHM around the principal outward crest.','R04_actual_FWHM_model_mm':nw,'R03_response_FWHM_same_actual_field_model_mm':ow,'width_ratio':nw/ow,'R04_peak_intensity':npeak,'R03_response_peak_intensity':opeak,'R04_crest_radius_model_mm':nradius,'R03_crest_radius_model_mm':oradius,'R04_actual_FWHM_pixels_at_1024_fullmodel':nw*1024/726.25,'peak_source_crest_RGB':[40,235,248],'ridge_kernel_support_width_mm':1.7,'bilinear_grid_filtering_can_broaden_kernel_support':True,'background_source_RGB':[0,0,0],'glow_or_bloom_added':False,'metric_not_physical_projector_validation':True}
(D/'Actual_Crest_Width_Comparison_QA.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
