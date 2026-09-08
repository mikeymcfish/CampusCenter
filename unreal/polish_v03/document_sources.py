from pathlib import Path
import hashlib,json
root=Path(__file__).parent
files=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (root/'assets').rglob('*.jpg')]
(root/'assets/SOURCES.json').write_text(json.dumps({'asset':'ambientCG Wood049','source':'https://ambientcg.com/view?id=Wood049','download':'https://ambientcg.com/get?file=Wood049_2K-JPG.zip','license':'CC0','physical_size_m':[.8,.8],'usage':'Native Unreal oak materials; existing UVs retiled 3 x 1.5 to preserve physical grain scale','files':files},indent=2))
