from pathlib import Path
import json,hashlib
R=Path(__file__).parent;B=R.parent/'CampusCenter-print-furniture-v26-r01';rows=[]
for family,stem in [('ground_furnished','Ground_Furnished'),('ground_enclosed','Ground_Enclosed'),('ground_acrylic','Ground_Acrylic')]:
 for suffix in ['.stl','.step']:
  p=R/family/(stem+suffix);old=B/family/p.name;sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==hashlib.sha256(old.read_bytes()).hexdigest();rows.append({'file':str(p.relative_to(R)),'sha256':sha,'byte_identical_to_validated_R01':True})
 receipt=json.loads((R/family/'step_validation.json').read_text());validation=json.loads((R/family/'validation.json').read_text());assert abs(receipt['reopened_volume_mm3']-validation['volume_mm3'])/validation['volume_mm3']<1e-6
(R/'reused_ground_step_proof.json').write_text(json.dumps({'files':rows,'reason':'Ground geometry unchanged; retain exact independently reopened R01 STEP exports and receipts.'},indent=2));print('REUSED_GROUND_STEPS_VERIFIED')
