from inspect_receiver import *
import zipfile,datetime

root=ROOT;archive=root/'CampusCenter_Tron_WallCaps_UV02_T01_Test.zip'
files=[]
for directory in ['deliverables','source','qa','receiver_copy','cache']:
    for p in (root/directory).rglob('*'):
        if p.is_file() and p.suffix not in ['.pyc','.blend1'] and p.name not in ['package.log']:
            files.append(p)
files.extend(root/p for p in ['READ_ME.txt','camera_mapping.npz'])
# All producers and verification runs have ended before packaging. Hash the
# stable files here, including supporting caches, instead of a still-open log.
hashes={str(p.relative_to(root)).replace('\\','/'):sha(p) for p in sorted(files)}
(root/'SHA256.json').write_text(json.dumps(hashes,indent=2))
(root/'SHA256SUMS.txt').write_text('\n'.join(f'{h}  {p}' for p,h in hashes.items())+'\n')
files.extend(root/p for p in ['SHA256.json','SHA256SUMS.txt'])
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for p in sorted(files):z.write(p,str(p.relative_to(root)))
with zipfile.ZipFile(archive) as z:
    bad=z.testzip();assert bad is None
manifest={'status':'Complete isolated UV02 wall-cap first test; ready for parent review and sole publisher handoff',
 'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'files_in_archive':len(files),
 'mapped_camera_MP4':str(root/'deliverables/Tron_WallCaps_UV02_FrontNormal_Mapped_1024_10s24.mp4'),
 'atlas_input_MOV':str(root/'deliverables/Tron_WallCaps_UV02_Atlas_8192_10s24_Lossless.mov'),
 'read_me':str(root/'READ_ME.txt'),'hash_manifest':str(root/'SHA256.json'),'final_QA':str(root/'qa/Final_Media_QA.json'),
 'static_selection':str(root/'deliverables/WallCaps_Static_FrontNormal_Mapped_1024.png'),
 'oblique_selection_diagnostic':str(root/'deliverables/WallSelection_Oblique_DIAGNOSTIC_1024.png'),
 'geometry_and_UV_edits':[],'receiver_SHA256':sha(OBJ),'physical_configuration':'Five unchanged P02 1:100 tiles plus P03 B3 fireplace',
 'coverage':'Full-height opaque wall tops only. Vertical faces remain dark under assumed front-normal +Z view. Shorter partitions and fireplace excluded in this conservative first test.',
 'source_and_worker_outputs_preserved':True,'GitHub_push':False,'MadMapper_playback_verified':False,'physical_projection_verified':False,
 'remaining_physical_work':['Confirm real model orientation and calibrate one projector','Verify cap-only coverage and native 8192 qtrle playback on actual setup'],
 'sole_publisher_thread':'01a0f763-261e-7288-bd51-e736fd8b50fe'}
(root/'TRON_T01_HANDOFF.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2),flush=True)
