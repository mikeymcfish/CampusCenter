import os as _publication_os
def _publication_path(name, suffix):
 root=_publication_os.environ[name]
 return root.replace('\\','/').rstrip('/')+'/'+suffix

import pathlib,ctypes,json,hashlib,time,multiprocessing
from ctypes import wintypes
r=pathlib.Path(__file__).parent.resolve();src=pathlib.Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_Quest3_PC_VR_R01/Runtime/Windows/CampusCenter/Binaries/Win64/CampusCenter.exe'));target=r/'project/Binaries/Win64/CampusCenter.exe';size=16*1024*1024
class IN(ctypes.Structure):_fields_=[('start',ctypes.c_void_p),('size',ctypes.c_size_t),('editable',wintypes.BOOL)]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def worker(i):
 d=ctypes.WinDLL('msdelta.dll',use_last_error=True);d.CreateDeltaW.argtypes=[ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,wintypes.LPCWSTR,wintypes.LPCWSTR,wintypes.LPCWSTR,wintypes.LPCWSTR,IN,ctypes.c_void_p,wintypes.DWORD,wintypes.LPCWSTR];d.CreateDeltaW.restype=wintypes.BOOL;d.ApplyDeltaW.argtypes=[ctypes.c_uint64,wintypes.LPCWSTR,wintypes.LPCWSTR,wintypes.LPCWSTR];d.ApplyDeltaW.restype=wintypes.BOOL
 with src.open('rb') as f:f.seek(i*size);s=f.read(size)
 with target.open('rb') as f:f.seek(i*size);t=f.read(size)
 scratch=r/'delta-scratch-final'/str(i);scratch.mkdir(parents=True,exist_ok=False);a=scratch/'source.bin';b=scratch/'target.bin';v=scratch/'verified.bin';a.write_bytes(s);b.write_bytes(t);p=r/'overlay/NativeChunksFinal'/('chunk-%02d.msdelta'%i)
 assert d.CreateDeltaW(1,0,0,str(a),str(b),None,None,IN(),None,0,str(p)),ctypes.get_last_error();assert d.ApplyDeltaW(0,str(a),str(p),str(v)),ctypes.get_last_error();assert v.read_bytes()==t
 return {'path':'NativeChunks/'+p.name,'source_offset':i*size,'source_bytes':len(s),'target_bytes':len(t),'bytes':p.stat().st_size,'sha256':sha(p)}
if __name__=='__main__':
 out=r/'overlay/NativeChunksFinal';out.mkdir(exist_ok=False);assert sha(src)=='20adab2cd975e19d325adbe607b907cfffa2bd3e775b01c51a68f695bfdf915a';start=time.monotonic();count=(target.stat().st_size+size-1)//size;rows=[]
 with multiprocessing.Pool(4) as pool:
  for row in pool.imap_unordered(worker,range(count)):rows.append(row);print('Verified final chunk',row['path'],row['bytes'],flush=True)
 rows.sort(key=lambda x:x['source_offset']);recon=r/'roundtrip-final-CampusCenter.exe';assert not recon.exists()
 with recon.open('wb') as f:
  for i in range(count):f.write((r/'delta-scratch-final'/str(i)/'verified.bin').read_bytes())
 assert sha(recon)==sha(target)
 d={'base_exe_sha256':sha(src),'target_exe_sha256':sha(target),'target_bytes':target.stat().st_size,'chunks':rows,'delta_bytes':sum(x['bytes'] for x in rows),'roundtrip_exact':True,'elapsed_seconds':time.monotonic()-start,'implementation':'Windows msdelta RAW chunks, four isolated workers, final SHA-256 exact; Opt-in projector OSC sender; original grip/trigger native code unchanged'};(r/'final-chunked-binary-delta-proof.json').write_text(json.dumps(d,indent=2));print('Final bytes',d['delta_bytes'])
