from pathlib import Path
import json,shutil,hashlib
r=Path(__file__).resolve().parent;p=r/'payload';p.mkdir(exist_ok=True)
delta=json.loads((r/'final-chunked-binary-delta-proof.json').read_text())
base=json.loads((r.parent/'quest3-pcvr-r01/payload/quest-manifest.json').read_text())
metadata=json.loads((r/'metadata-overlay/overlay-files.json').read_text())
for row in delta['chunks']:
    dst=p/row['path'];dst.parent.mkdir(exist_ok=True);shutil.copy2(r/'overlay/NativeChunksFinal'/Path(row['path']).name,dst)
for row in metadata:shutil.copy2(r/'metadata-overlay'/row['path'],p/row['path'])
manifest=dict(revision='ProjectorSenderR01',base_exe_sha256=delta['base_exe_sha256'],target_exe_sha256=delta['target_exe_sha256'],target_bytes=delta['target_bytes'],chunks=delta['chunks'],base_files=base['base_files'],optional_quest_files=[dict(path='CampusCenter/Content/Paks/'+x['path'],bytes=x['bytes'],sha256=x['sha256']) for x in base['overlay_files']],overlay_files=metadata,map=base['map'],vive_inherited_arguments='CampusCenter /Game/Campus/Maps/CampusCenter_Vive_R29_TrophyTrainerGymCorrections_r02 -DisablePlugins=MetaHumanCrowdContent -vr -fullscreen -ResX=1920 -ResY=1080 -ExecCmds="r.ScreenPercentage 50,stat fps"',contract_sha256='32470ae57a97e8f4a8911524f0f8fd28a95a8b105d6be7643c8868037d81a3f4',no_push=True)
(p/'sender-manifest.json').write_text(json.dumps(manifest,indent=2));print(delta['delta_bytes'],len(base['base_files']),len(metadata))
