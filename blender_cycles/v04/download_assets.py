from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures
R=Path(__file__).parent/'assets';jobs=[]
for key,meta in [('potted_plant_01','plant_files.json'),('shrub_03','shrub_files.json'),('grass_medium_01','grass_files.json')]:
 d=json.loads((R/meta).read_text());entry=d['blend']['2k']['blend']
 jobs.append((R/key/(key+'.blend'),entry))
 for path,info in entry.get('include',{}).items():jobs.append((R/key/path,info))
entry=json.loads((R/'hdri_files.json').read_text())['hdri']['4k']['hdr'];jobs.append((R/'greenwich_park_4k.hdr',entry))
def get(job):
 p,info=job;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists() or hashlib.md5(p.read_bytes()).hexdigest()!=info['md5']:urllib.request.urlretrieve(info['url'],p)
 assert hashlib.md5(p.read_bytes()).hexdigest()==info['md5']
 return {'file':str(p.relative_to(R)),'url':info['url'],'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'license':'CC0'}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(get,jobs))
(R/'DOWNLOADS.json').write_text(json.dumps(rows,indent=2));print('Downloaded and checked',len(rows),'files',sum(r['bytes'] for r in rows),'bytes')
