from pathlib import Path
import re,json,subprocess,hashlib,argparse
from PIL import Image
import sys
R=Path(__file__).parent;sys.path.insert(0,str(R));from production_common import COPY,np
ap=argparse.ArgumentParser();ap.add_argument('--suffix',default='');args=ap.parse_args();suffix=('_'+args.suffix) if args.suffix else ''
D=R/'madmapper_highlight_H04/deliverables';O=D/('Mapped_Overview'+suffix);O.mkdir(exist_ok=True)
ff=Path(__import__('os').environ.get('CC_FFMPEG','ffmpeg'));clips=[];pages=[];timeline=[];seconds=0
for sid,(title,body) in enumerate(COPY['spaces'],1):
    slug=re.sub(r'[^A-Za-z0-9]+','_',title).strip('_');folder=D/slug;q=json.loads((folder/'Compact_Mapped_Preview_QA.json').read_text());assert q['all_preview_frames_decoded'];clips.append(Path(q['file']))
    for page,png in enumerate(sorted(folder.glob('*_Page_*_Mapped_1024_Viewing.png')),1):
        pages.append(png);timeline.append({'official_title':title,'stop_id_metadata_only':f'HS{sid:02d}','page':page,'start_seconds':seconds,'end_seconds':seconds+10,'source_still':str(png.relative_to(D))});seconds+=10
assert len(pages)==30 and seconds==300
filelist=O/'Overview_Concat_Source_List.txt';filelist.write_text('\n'.join("file '"+p.as_posix().replace("'","'\\''")+"'" for p in clips)+'\n',encoding='utf-8')
target=O/('Tour_H04_All13_30Pages'+suffix+'_Mapped_1024_Overview.mp4');assert not target.exists()
subprocess.run([str(ff),'-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(filelist),'-c','copy','-movflags','+faststart',str(target)],check=True)
probe=json.loads(subprocess.check_output([str(ff.with_name('ffprobe.exe')),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(target)]));assert int(probe['streams'][0]['nb_read_frames'])==6000 and abs(float(probe['streams'][0]['duration'])-300)<.01
subprocess.run([str(ff),'-hide_banner','-loglevel','error','-i',str(target),'-f','null','-'],check=True)
subprocess.run([str(ff),'-hide_banner','-loglevel','error','-i',str(target),'-vf',r'select=eq(mod(n\,200)\,100)','-fps_mode','vfr',str(O/'Overview_Page_%02d_Actual_Decoded.png')],check=True)
decoded=sorted(O.glob('Overview_Page_*_Actual_Decoded.png'));assert len(decoded)==30;errors=[]
for info,src,out in zip(timeline,pages,decoded):
    a=np.asarray(Image.open(src).convert('RGB'),np.int16);b=np.asarray(Image.open(out).convert('RGB'),np.int16);diff=np.abs(a-b);mean=float(diff.mean());assert mean<2
    errors.append({'page':len(errors)+1,'actual_decoded_midpoint':out.name,'mean_absolute_RGB_byte_error_from_native_mapped_preview':mean,'max_RGB_byte_error':int(diff.max()),'no_reencoding_during_concatenation':True});info['actual_decoded_midpoint']=out.name
q={'status':'PASS: all6000 frames decode;30 actual decoded page midpoints extracted and compared','file':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'width':1024,'height':846,'fps':20,'frames':6000,'duration_seconds':300,'stops':13,'pages':30,'each_page_hold_seconds':10,'actual_native_mapped_source_images':True,'raw_projection_atlas_movie':False,'all_frames_fully_decoded':True,'preserves_existing_compact_bitstreams_without_reencoding':True,'page_codec_checks':errors,'timeline':timeline,'visual_review_pending':True,'physical_projection_or_readability_verified':False,'probe':probe}
(O/'Mapped_Overview_QA.json').write_text(json.dumps(q,indent=2));print(json.dumps({k:q[k] for k in ['status','file','bytes','sha256','pages','duration_seconds']},indent=2),flush=True)
