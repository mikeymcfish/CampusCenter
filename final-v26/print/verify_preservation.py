from pathlib import Path
import json,hashlib
R=Path(__file__).parent;B=R.parent/'CampusCenter-print-r25-r01';manifest=json.loads((B/'delivery_manifest.json').read_text());checked=[]
for item in manifest:
 p=B/item['file'];actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==item['sha256'],item['file'];checked.append(item['file'])
for p,sha in [(Path(r'C:\Users\mikef\Documents\Codex\2026-09-30\task\CampusCenter-new-plans\scene\Campus_Center_New_Plans_Audit_v25.blend'),'c39e7b686b56603f38500f1b22d6ebbb459362e66fa255da1a4b315e4a216721'),(Path(json.loads((R/'furniture_source.json').read_text())['source']),json.loads((R/'furniture_source.json').read_text())['sha256'])]:assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
previous=R.parent/'CampusCenter-print-furniture-v26-r01';prior=json.loads((previous/'delivery_manifest.json').read_text())
for item in prior:assert hashlib.sha256((previous/item['file']).read_bytes()).hexdigest()==item['sha256'],item['file']
(R/'preservation.json').write_text(json.dumps({'v25_baseline_files_matching_original_delivery_manifest':len(checked),'furniture_R01_files_matching_original_delivery_manifest':len(prior),'all_match':True,'source_v25_unchanged':True,'source_B05_unchanged':True,'files':checked},indent=2));print('PRESERVED',len(checked),len(prior))
