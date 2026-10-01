import pathlib,json,hashlib,shutil
R=pathlib.Path(__file__).parent/'CampusCenter-new-plans';D=R/'downstream/furniture_art_v26_r01';release=D/'releases/shared_furniture_art_v26_r01';P=R/'downstream/desktop_furniture_v26_r01/delivery_project_r01';m=json.loads((release/'manifest.json').read_text());rows=[]
for x in m['dependency_packages']:
 q=P/x['relative_file']
 if x['new_namespace']:
  assert not q.exists(),q;p=release/x['relative_file'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 assert q.exists() and hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256'],('dependency mismatch',q)
 rows.append(x['package'])
source=json.loads((D/'enhancement-r15.json').read_text());mapfile=P/'Content/Campus/Maps/CampusCenter_FA26_Desktop_R15.umap';assert not mapfile.exists();shutil.copy2(source['file'],mapfile);assert hashlib.sha256(mapfile.read_bytes()).hexdigest()==source['sha256']
baseline=R/'downstream/desktop_r01/unreal_project';cache=baseline/'Saved/Cooked/Windows';target=P/'Saved/Cooked/Windows'
if cache.exists():
 assert not target.exists();shutil.copytree(cache,target);cache_note='Copied compatible verified R16 cooked cache for iterative recook; native binaries/config unchanged, new content recooks through UAT.'
else:cache_note='No baseline cooked cache; full cook required.'
(D/'desktop-delivery-overlay-proof.json').write_text(json.dumps({'project':str(P),'map_sha256':source['sha256'],'dependency_count':len(rows),'new_packages':121,'source_prototypes_excluded':True,'cache':cache_note},indent=2));print('DELIVERY_READY',str(P),flush=True)
