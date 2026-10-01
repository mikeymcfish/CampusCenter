from pathlib import Path
import json,hashlib,os,winreg,datetime
r=Path(__file__).resolve().parent;p=r.parent/'CampusCenter-vive/unreal/unreal_project';backup=r/'original-r06-state';backup.mkdir(exist_ok=True)
paths=['CampusCenter.uproject','Config/DefaultInput.ini','Config/DefaultEngine.ini']
rows=[]
for relative in paths:
 data=(p/relative).read_bytes();target=backup/relative;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(data);rows.append({'path':relative,'sha256':hashlib.sha256(data).hexdigest()})
descriptor=json.loads((p/'CampusCenter.uproject').read_text());assert not any(x['Name']=='OpenXR' for x in descriptor['Plugins']);descriptor['Plugins'].append({'Name':'OpenXR','Enabled':True});(p/'CampusCenter.uproject').write_text(json.dumps(descriptor,indent=2)+'\n')
input_file=p/'Config/DefaultInput.ini';text=input_file.read_text();assert 'DefaultMappingContexts=' not in text
text+='\n[/Script/EnhancedInput.EnhancedInputDeveloperSettings]\nbEnableDefaultMappingContexts=True\n+DefaultMappingContexts=(InputMappingContext="/Game/Campus/ViveTriggerWalkR01/IMC_ViveTriggerWalk.IMC_ViveTriggerWalk",Priority=0,bAddImmediately=False,bRegisterWithUserSettings=False)\n';input_file.write_text(text)
runtime={}
for root,key,name in [(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\Khronos\OpenXR\1','ActiveRuntime'),(winreg.HKEY_CURRENT_USER,r'SOFTWARE\Khronos\OpenXR\1','ActiveRuntime'),(winreg.HKEY_CURRENT_USER,r'SOFTWARE\Valve\Steam','SteamPath'),(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\WOW6432Node\Valve\Steam','InstallPath')]:
 try:
  with winreg.OpenKey(root,key) as handle:runtime[key+'\\'+name]=winreg.QueryValueEx(handle,name)[0]
 except OSError as error:runtime[key+'\\'+name]={'error':str(error),'winerror':error.winerror}
runtime['XR_RUNTIME_JSON_environment']=os.environ.get('XR_RUNTIME_JSON');runtime['default_SteamVR_directory_exists']=Path(r'C:/Program Files (x86)/Steam/steamapps/common/SteamVR').exists()
(r/'project-activation.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'backup':str(backup),'before_files':rows,'allowed_changes':['Enable installed OpenXR project plugin, dependency XRBase automatic','Register existing trigger context for OpenXR action construction, no automatic activation outside helper map','New map-only local tracking origin initialization and VR launcher flag'],'runtime_read_only':runtime,'system_changes':False},indent=2))
