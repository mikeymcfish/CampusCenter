from pathlib import Path
import csv,json,statistics,math,shutil
csv.field_size_limit(10000000)
from PIL import Image
root=Path(__file__).parent;app=root.parent/'unreal_delivery/Windows/Engine/Saved'
files=sorted((app/'Profiling/CSV').glob('*.csv'))[-3:]
out={'gpu':'NVIDIA GeForce RTX 4090','output_resolution':[1920,1080],'screen_percentage':100,'mode':'packaged Development, DX12, Lumen hardware RT, offscreen real-time rendering, uncapped, VSync off','warmup_frames_discarded':300,'normal_exploration_cap_fps':60,'results':[]}
for path,mapname in zip(files,['Commons','Innovation Lab','Upper commons']):
 with path.open(newline='') as f:
  reader=csv.DictReader(f);rows=[]
  for row in reader:
   try:
    dt=float(row.get('FrameTime',''))
    if dt>0:rows.append(row)
   except (ValueError,TypeError):pass
 rows=rows[300:];values=[float(r['FrameTime']) for r in rows];v=sorted(values)
 gpu=[float(r['GPUTime']) for r in rows if r.get('GPUTime') and float(r['GPUTime'])>0]
 result={'area':mapname,'source_csv':path.name,'measured_frames':len(values),'average_fps':round(1000/statistics.mean(values),1),'median_fps':round(1000/statistics.median(values),1),'p95_frame_ms':round(v[int(.95*(len(v)-1))],2),'one_percent_low_fps':round(1000/statistics.mean(v[-max(1,math.ceil(len(v)*.01)):]),1),'median_gpu_ms':round(statistics.median(gpu),2)}
 out['results'].append(result)
 evidence=root/'performance_evidence';evidence.mkdir(exist_ok=True);shutil.copy2(path,evidence/path.name)
shots=sorted((app/'Screenshots/Windows').glob('ScreenShot*.png'))[-3:]
out['resolution_evidence']=[]
for p in shots:
 with Image.open(p) as im:
  assert im.size==(1920,1080),im.size
  out['resolution_evidence'].append({'file':p.name,'pixels':list(im.size)})
(root/'performance.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
