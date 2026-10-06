import os as _publication_os
def _publication_path(name, suffix):
 root=_publication_os.environ[name]
 return root.replace('\\','/').rstrip('/')+'/'+suffix

from pathlib import Path
import subprocess,json,hashlib,os
r=Path(__file__).resolve().parent
source=Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_Quest3_PC_VR_R01/Runtime/Windows'))
qa=Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_ProjectorSender_R01/InstallerQA'));qa.mkdir(exist_ok=True)
manifest=json.loads((r/'payload/sender-manifest.json').read_text())
shell='C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
script=r/'payload/ProjectorSender.ps1';reports=[]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda:f.read(8*1024*1024),b''):h.update(x)
    return h.hexdigest()
def run(name,args,good):
    result=subprocess.run([shell,'-NoProfile','-File',str(script)]+args,capture_output=True,text=True)
    (r/('installer-'+name+'.log')).write_text(result.stdout+result.stderr)
    assert (result.returncode==0)==good,(name,result.stderr)
    reports.append(dict(name=name,exit=result.returncode,expected_success=good));(r/'installer-validation.json').write_text(json.dumps(dict(cases=reports),indent=2));print(name,result.returncode,flush=True)
review=_publication_path('CC_REVIEW_ROOT', 'CampusCenter_ProjectorSender_R01/InstalledReview/Windows')
run('existing-refused',['-Action','Install','-SourceWindows',str(source),'-TargetWindows',review],False)
unknown=qa/'UnknownSource';assert not unknown.exists()
for row in manifest['base_files']+manifest['optional_quest_files']:
    dst=unknown/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);os.link(source/row['path'],dst)
(unknown/'CampusCenter/Content/Paks/Unknown.pak').write_text('Own rejection fixture only')
unknown_target=qa/'MustNotBeCreated';run('unknown-refused',['-Action','Install','-SourceWindows',str(unknown),'-TargetWindows',str(unknown_target)],False);assert not unknown_target.exists()
rollback=qa/'Rollback/Windows';run('rollback-install',['-Action','Install','-SourceWindows',str(source),'-TargetWindows',str(rollback)],True)
run('rollback-verify',['-Action','Verify','-TargetWindows',str(rollback)],True)
run('rollback',['-Action','Rollback','-TargetWindows',str(rollback)],True)
for row in manifest['base_files']+manifest['optional_quest_files']:assert sha(rollback/row['path'])==row['sha256'],row['path']
assert not (rollback/'projector-sender-installed.json').exists()
assert all(not (rollback/'CampusCenter/Content/Paks'/row['path']).exists() for row in manifest['overlay_files'])
for row in manifest['base_files']+manifest['optional_quest_files']:assert sha(source/row['path'])==row['sha256'],row['path']
final=dict(passed=True,cases=reports,rollback_native_and_all_48_original_files_exact=True,source_all_48_files_unchanged=True,review_runtime_preserved=review,unknown_destination_not_created=True)
(r/'installer-validation.json').write_text(json.dumps(final,indent=2));print(json.dumps(final),flush=True)
