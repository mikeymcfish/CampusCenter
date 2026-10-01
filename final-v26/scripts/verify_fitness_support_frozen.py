import pathlib,hashlib,json,time
R=pathlib.Path(__file__).parent/'CampusCenter-new-plans';source=R/'downstream/desktop_r01/unreal_project';target=R/'downstream/desktop_furniture_v26_r01/unreal_project';D=R/'downstream/furniture_art_v26_r01';rows=[];start=time.time()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while True:
   b=f.read(4*1024*1024)
   if not b:break
   h.update(b)
 return h.hexdigest()
files=[source/'CampusCenter.uproject']
for name in ['Binaries','Build','Config','Content','Plugins']:files.extend(p for p in (source/name).rglob('*') if p.is_file())
for p in files:
 rel=p.relative_to(source);q=target/rel;before=sha(p);after=sha(q) if q.exists() else None;rows.append({'file':str(rel).replace('\\','/'),'sha256':before,'copied_match':before==after})
failure=[r for r in rows if not r['copied_match']];record={'source':str(source),'target':str(target),'checked_files':len(rows),'elapsed_s':time.time()-start,'failures':failure,'rows':rows,'scope':'All copied baseline bytes after fitness support correction. New namespaces excluded by enumeration from frozen R16 source. Original source is read-only.'};(D/'fitness_support_patch_r01/frozen-baseline-byte-proof.json').write_text(json.dumps(record,indent=2));print('Baseline copied files',len(rows),'failures',len(failure),flush=True);assert not failure
