import os as _publication_os
def _publication_path(name, suffix):
 root=_publication_os.environ[name]
 return root.replace('\\','/').rstrip('/')+'/'+suffix

from pathlib import Path
import json,os,shutil,hashlib
r=Path(__file__).resolve().parent
source=Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_ProjectorSender_R01/Runtime/Windows'))
target=Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_ProjectorSender_R01/ShippingQA/Windows'))
proof=json.loads((r/'runtime-staging-proof.json').read_text());rows=proof['base_files']
rows+= [dict(path='CampusCenter/Content/Paks/'+x['path'],sha256=x['sha256']) for x in json.loads((r/'metadata-overlay/overlay-files.json').read_text())]
assert not target.exists()
native='CampusCenter/Binaries/Win64/CampusCenter.exe'
shipping=r/'project/Binaries/Win64/CampusCenter-Win64-Shipping.exe'
for row in rows:
    dst=target/row['path'];dst.parent.mkdir(parents=True,exist_ok=True)
    if row['path']==native:shutil.copy2(shipping,dst)
    else:os.link(source/row['path'],dst)
report=dict(target=str(target),new_native_sha256=hashlib.sha256(shipping.read_bytes()).hexdigest(),files=len(rows),only_native_configuration_differs=True)
(r/'shipping-runtime-staging.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
