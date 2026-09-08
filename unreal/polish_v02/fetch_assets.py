from pathlib import Path
import urllib.request,zipfile,hashlib,json
root=Path(__file__).parent/'assets';root.mkdir(exist_ok=True)
items=[('Fabric030','https://ambientcg.com/get?file=Fabric030_1K-JPG.zip','https://ambientcg.com/view?id=Fabric030','CC0'),('PaintedPlaster017','https://ambientcg.com/get?file=PaintedPlaster017_1K-JPG.zip','https://ambientcg.com/view?id=PaintedPlaster017','CC0'),('trophy_5.blend','https://opengameart.org/sites/default/files/trophy_5.blend','https://opengameart.org/content/trophy','CC0, JeremyWoods')]
records=[]
for name,url,page,license in items:
 p=root/(name if name.endswith('.blend') else name+'.zip')
 if not p.exists():
  req=urllib.request.Request(url,headers={'User-Agent':'CampusCenterAssetPreparation/1.0'})
  with urllib.request.urlopen(req,timeout=90) as r:p.write_bytes(r.read())
 if p.suffix=='.zip':
  with zipfile.ZipFile(p) as z:
   for entry in z.infolist():
    target=(root/name/entry.filename).resolve()
    assert target.is_relative_to((root/name).resolve())
   z.extractall(root/name)
 records.append({'name':name,'source':page,'download':url,'license':license,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(root/'SOURCES.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
