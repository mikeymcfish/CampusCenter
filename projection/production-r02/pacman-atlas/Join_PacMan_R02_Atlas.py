import json,hashlib,os
from pathlib import Path
root=Path(__file__).resolve().parent
m=json.loads((root/'RAW_ATLAS_JOIN_MANIFEST.json').read_text())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(4*1024*1024):h.update(b)
 return h.hexdigest()
output=root/m['output_file']
if output.exists():
 if output.stat().st_size==m['output_bytes'] and digest(output)==m['output_sha256']:print('Existing movie already verified.');raise SystemExit(0)
 raise SystemExit('Output exists with different bytes; preserve it and choose another folder.')
for pin in m['parts']:
 p=root/pin['file']
 if p.stat().st_size!=pin['bytes'] or digest(p)!=pin['sha256']:raise SystemExit('Part verification failed: '+p.name)
temporary=output.with_name(output.name+'.joining')
h=hashlib.sha256();count=0
with temporary.open('xb') as dst:
 for pin in m['parts']:
  with (root/pin['file']).open('rb') as src:
   while b:=src.read(4*1024*1024):dst.write(b);h.update(b);count+=len(b)
if count!=m['output_bytes'] or h.hexdigest()!=m['output_sha256']:raise SystemExit('Joined bytes failed verification; .joining file preserved.')
os.rename(temporary,output)
print('Verified original lossless movie:',output.name)
