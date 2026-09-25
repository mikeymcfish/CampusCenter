from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent.parent
repo=Path('P:/_code/CampusCenter/unreal')
data=json.loads((root/'architect_finishes_v01/delivery_validation.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
errors=[];files=[]
for rel in data['dependency_files']:
 a=root/'unreal_project'/rel;b=repo/'unreal_project'/rel
 h=sha(a)
 if not b.is_file() or sha(b)!=h:errors.append(rel)
 files.append({'path':'unreal_project/'+rel,'bytes':a.stat().st_size,'sha256':h})
originals={
 'output_v18/Campus_Center_Textured.blend':'df9a8c1c453a1e4b2885c9e017a2bee4bbd4b811b1078172fa146e161ec09308',
 'unreal_project/Content/Campus/Maps/CampusCenter_Dusk.umap':'6859ce249fa867ef9f139e3f0568ee72bd74e6355c10c5011aa8b7288bf51255'}
for rel,expected in originals.items():
 if sha(root/rel)!=expected:errors.append('Original changed: '+rel)
result={'verified_asset_count':len(files),'copied_asset_errors':errors,'originals_unchanged':not any(x.startswith('Original') for x in errors),'files':files}
(repo/'ARCHITECT_ASSET_MANIFEST.json').write_text(json.dumps(result,indent=2))
(root/'architect_finishes_v01/github_copy_validation.json').write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
print({k:v for k,v in result.items() if k!='files'})
assert not errors,errors
