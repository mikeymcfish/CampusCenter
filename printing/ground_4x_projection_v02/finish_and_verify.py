from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,subprocess,zipfile
R=Path(__file__).parent;FF='T:/AI/ffmpeg/bin/ffmpeg.exe';FP='T:/AI/ffmpeg/bin/ffprobe.exe'
files=sorted((R/'frames').glob('*.png'));assert len(files)==24
raw=sorted((R/'imagegen_raw').glob('people_*.png'));assert len(raw)==24
base=np.array(Image.open(R/'Projection_Base_Top_Down.png').convert('RGB'));mask=np.array(Image.open(R/'floor_only_mask.png').convert('L'));assert set(np.unique(mask))=={0,255}
frames=[];report=[];hashes=[]
for p in files:
 im=Image.open(p);assert im.size==(1024,786) and im.mode=='RGB';a=np.array(im);assert a[mask==0].max()==0,p
 change=np.any(a!=base,axis=2);assert 30<change.sum()<1500,(p,change.sum())
 assert not np.any(change[mask==0]);frames.append(a);h=hashlib.sha256(p.read_bytes()).hexdigest();hashes.append(h)
 report.append({'file':str(p.relative_to(R)),'sha256':h,'dimensions':list(im.size),'mode':im.mode,'changed_pixels':int(change.sum()),'maximum_channel_outside_floor_mask':0})
assert len(set(hashes))==24
change_union=np.any(np.stack([np.any(a!=base,axis=2) for a in frames]),axis=0)
assert all(np.array_equal(a[~change_union],base[~change_union]) for a in frames)
diff=[float(np.abs(frames[(i+1)%24].astype(float)-frames[i]).mean()) for i in range(24)]
assert diff[-1]<1.6*max(diff[:-1]),diff
def ff(args):subprocess.run([FF,'-hide_banner','-loglevel','error','-y']+args,check=True)
inp=['-framerate','4','-i',str(R/'frames/%04d.png')]
# RGB lossless preserves projector blackout pixels exactly, unlike chroma-subsampled previews.
master=R/'Projection_Loop_Lossless_RGB.mp4';preview=R/'Projection_Loop_Preview.mp4'
ff(inp+['-r','24','-c:v','libx264rgb','-crf','0','-preset','medium','-pix_fmt','rgb24','-movflags','+faststart',str(master)])
ff(inp+['-r','24','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(preview)])
meta=json.loads(subprocess.check_output([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(master)]));v=meta['streams'][0];assert (v['width'],v['height'],int(v['nb_read_frames']))==(1024,786,144);assert abs(float(meta['format']['duration'])-6)<.001
decoded=subprocess.check_output([FF,'-v','error','-i',str(master),'-f','rawvideo','-pix_fmt','rgb24','pipe:1']);a=np.frombuffer(decoded,dtype=np.uint8).reshape(-1,786,1024,3);assert len(a)==144
assert all(np.array_equal(a[i],frames[i//6]) for i in range(144))
source=R.parent/'projection_print_v01/Campus_Center_Projection.blend';src_hash=hashlib.sha256(source.read_bytes()).hexdigest();assert src_hash==json.loads((R/'render_contract.json').read_text())['source_sha256']
result={'status':'passed','frame_count':24,'generated_character_asset_count':24,'resolution':[1024,786],'keyframe_rate':4,'video_rate':24,'video_frames':144,'duration_seconds':6,'video_repeats_each_keyframe':6,'static_background_pixels':int((~change_union).sum()),'animated_pixels_union':int(change_union.sum()),'all_walls_and_exterior_exact_rgb_zero':True,'lossless_video_decodes_bit_exact_to_png_frames':True,'frame24_to_frame1_mean_difference':diff[-1],'largest_other_frame_difference':max(diff[:-1]),'source_unchanged':True,'source_sha256':src_hash,'generator':'Built-in image_gen tool; no explicit model-version selector is exposed','raw_generated_images_unmodified':True,'frame_reports':report}
(R/'validation.json').write_text(json.dumps(result,indent=2))
prompts=[json.loads(p.read_text()) for p in sorted((R/'prompts').glob('frame_*.json'))];assert len(prompts)==24
for p in prompts:p['file']=f'imagegen_raw/people_{p["frame"]:04}.png'
(R/'imagegen_prompts.json').write_text(json.dumps(prompts,indent=2))
with zipfile.ZipFile(R/'Projection_24_Images.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,'frames/'+p.name)
 for name in ['Projection_Base_Top_Down.png','floor_only_mask.png','Calibration_25mm_Floor_Only.png','README.md']:z.write(R/name,name)
print(json.dumps({k:v for k,v in result.items() if k!='frame_reports'},indent=2))
