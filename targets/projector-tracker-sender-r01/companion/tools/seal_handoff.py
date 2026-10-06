from pathlib import Path
import json,hashlib,zipfile,datetime
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'deliverables'
rows=[]
for p in out.glob('*.zip'):
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        if 'Portable' in p.name:
            prefix='CampusCenterTracker_R01/'
            manifest=json.loads(z.read(prefix+'FILE_MANIFEST.json'))
            for name,info in manifest.items():
                data=z.read(prefix+name)
                assert len(data)==info['bytes'] and hashlib.sha256(data).hexdigest()==info['sha256'],name
    rows.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'zip_crc_verified':True})
q=json.loads((ROOT/'qa/QA_RESULTS.json').read_text())
s=json.loads((ROOT/'qa/portable/PORTABLE_SMOKE.json').read_text())
assert all(t['passed'] for t in q['tests']) and s['passed']
j={'status':'R01_COMPANION_PREPARED_SOFTWARE_VALIDATED_SIMULATOR_LIVE_GAME_AND_PHYSICAL_ACCEPTANCE_PENDING',
 'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'isolated_workspace':str(ROOT),'portable_folder':str(ROOT/'stage/CampusCenterTracker_R01'),
 'telemetry_contract':str(ROOT/'TELEMETRY_CONTRACT.md'),'contract_sha256':hashlib.sha256((ROOT/'TELEMETRY_CONTRACT.md').read_bytes()).hexdigest(),
 'address':'/campuscenter/player/v1','types':',issisfffffiii','bind':'127.0.0.1:9001',
 'profile':'campuscenter-r29-p02-sample-1-250-v1','registration':{'x':'(UE_X_cm+4700)/25','y':'(-UE_Y_cm+230)/25'},
 'P02_sample_source_sha256':'d14d518971fb4c5265544eb84ba0d2bdd0b620097afe12cdd8ab9a08e86fa032',
 'ground_behavior':'sharp dot','upstairs_behavior':'Gaussian blurred dot at same fixed XY',
 'hide_behavior':'invalid tracking, 500ms receiver monotonic timeout, outside exact foundation footprint',
 'software_qa':{'grouped_checks_passed':len(q['tests']),'failed':0,'build_warnings':0,'portable_winexe_exit_code':0,'bundled_runtime_used':s['local_dotnet_root'],'simulator_upstairs_accepted':s['tracking']['Accepted'],'simulation_evidence':True},
 'deliverables':rows,'screenshots':[str(ROOT/'qa/Companion_UI_simulator.png'),str(ROOT/'qa/evidence/Ground_sharp.png'),str(ROOT/'qa/evidence/Upstairs_blurred.png'),str(ROOT/'qa/portable/Portable_UI_upstairs.png')],
 'source_build_instructions':str(ROOT/'README.md'),'qa':str(ROOT/'QA.md'),
 'unreal_sender_owner':'01a0f36f-2c2f-74cd-a7a4-9f81894fe015','sole_GitHub_publisher':'01a0f763-261e-7288-bd51-e736fd8b50fe',
 'unreal_checkout_edited':False,'GitHub_pushed':False,'software_installed':False,'firewall_changed':False,'OS_display_settings_changed':False,
 'host_certificate_check':'No new localhost certificate: read-only host check found only existing expired 2024 certificate after SDK first-use message; no certificate was changed/deleted.',
 'remaining_blockers':['Unreal owner still building/integrating opt-in sender; actual packaged-game telemetry not tested by companion task.',
 'Tank exposed one display; actual secondary projector selection/disconnect/focus behavior needs equipment.',
 'Actual DPI transitions, physical P02 alignment, wall/glazing parallax, HMD tracking/floor/controls and sustained VR frame time need real testing.'],
 'publisher_requirements':['Publish companion as separate opt-in source/runtime target; do not replace/modify current R29/Quest/Vive/desktop/performance launchers.',
 'Use sealed ZIP hashes; keep private runtime and licenses with app; no install/admin/security/monitor changes.',
 'Coordinate sender schema/floor classification/package QA with Unreal owner; do not label simulator as packaged-game integration.',
 'No laser/MadMapper/UV02 assembly changes; P02 1:250 sample model registration stays explicit.']}
(out/'COMPANION_R01_PUBLISHER_HANDOFF.json').write_text(json.dumps(j,indent=2))
print(json.dumps(j,indent=2))
