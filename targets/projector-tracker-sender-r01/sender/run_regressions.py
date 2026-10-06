import os as _publication_os
def _publication_path(name, suffix):
 root=_publication_os.environ[name]
 return root.replace('\\','/').rstrip('/')+'/'+suffix

from pathlib import Path
import subprocess,json,shutil,hashlib
r=Path(__file__).resolve().parent
qa=r/'input-regression';qa.mkdir(exist_ok=True)
project=r/'project/CampusCenter.uproject'
quest_source=r.parent/'quest3-pcvr-r01/project/Content/Campus/ViveTriggerWalkR01/IMC_ViveTriggerWalk.uasset'
quest_target=r/'project/Content/Campus/ProjectorQA/IMC_ViveTriggerWalk.uasset'
quest_target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(quest_source,quest_target)
reports=[]
for name,file,report in [('grip','test_grips.py','grip-validation.json'),('trigger','test_input.py','input-validation.json'),('keyboard','test_keyboard.py','keyboard-validation.json'),('quest','test_touch.py','touch-validation.json')]:
    out=qa/name;out.mkdir(exist_ok=False)
    source=r.parent/('quest3-pcvr-r01' if name=='quest' else 'vr-grip-turn-r01')/file
    text=source.read_text().replace('CampusCenter_Vive_R27_R28_FinalReview_r01','CampusCenter_Vive_R29_TrophyTrainerGymCorrections_r02').replace("'map':'R28 retained map'","'map':'R29 current source, sender opt-in enabled'")
    if name=='quest':text=text.replace('/Game/Campus/ViveTriggerWalkR01/IMC_ViveTriggerWalk','/Game/Campus/ProjectorQA/IMC_ViveTriggerWalk')
    script=out/file;script.write_text(text)
    args=[_publication_path('CC_UE_ROOT', 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'),str(project),'-ExecutePythonScript='+str(script),'-CampusProjector','-CampusViveInputQA','-unattended','-NullRHI','-nosplash','-NoIni','-DisablePlugins=MetaHumanCrowdContent','-DDC=InstalledNoZenLocalFallback','-abslog='+str(out/'editor.log')]
    with (out/'console.log').open('w') as log:run=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
    # Restore the original settings if an editor plugin writes initialization metadata.
    for p in (r.parent/'vr-grip-turn-r01/project/Config').glob('*.ini'):shutil.copy2(p,r/'project/Config'/p.name)
    result=json.loads((out/report).read_text())
    reports.append(dict(name=name,editor_exit=run.returncode,report=str(out/report),passed=result.get('passed',False)))
    (qa/'summary.json').write_text(json.dumps(reports,indent=2));print(name,run.returncode,result.get('passed'),flush=True)
    assert run.returncode==0 and result.get('passed'),result
print('All four input suites passed with opt-in sender running.',flush=True)
