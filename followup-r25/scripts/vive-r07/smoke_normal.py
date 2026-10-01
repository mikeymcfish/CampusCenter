from pathlib import Path
import subprocess,time,json,ctypes
from ctypes import wintypes
r=Path(__file__).resolve().parent
b=r.parent/'CampusCenter-vive/review_build_vive_openxr_r07_r01/Windows'
exe=b/'CampusCenter/Binaries/Win64/CampusCenter.exe'
o=r/'packaged-normal';o.mkdir(exist_ok=True)
frozen=json.loads((r/'frozen-final.json').read_text());args=[str(exe),frozen['map'],'-DisablePlugins=MetaHumanCrowdContent','-game','-vr','-fullscreen','-ResX=1920','-ResY=1080','-ExecCmds=r.ScreenPercentage 50,stat fps','-nosplash','-abslog='+str(o/'runtime.log')]
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
p=subprocess.Popen(args,cwd=exe.parent,startupinfo=si);started=time.time()
(o/'launch.json').write_text(json.dumps({'pid':p.pid,'exe':str(exe),'arguments':args,'scope':'Normal launch with exact GitHub rendering/plugin exclusion flags, review map selection only; no Ghost, CSV or runtime activation.'},indent=2))
for i in range(30):
 time.sleep(10);assert p.poll() is None,'Premature exit during normal five-minute run';print('NORMAL_RUNNING',10*(i+1),flush=True)
assert p.poll() is None,'Exited before normal window close'
u=ctypes.windll.user32;windows=[]
u.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
u.IsWindowVisible.argtypes=[wintypes.HWND]
callback=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
def each(hwnd,lparam):
 pid=wintypes.DWORD();u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
 if pid.value==p.pid and u.IsWindowVisible(hwnd):windows.append(int(hwnd))
 return True
u.EnumWindows(callback(each),0)
assert windows,'No visible window owned by launched game; no forced termination'
u.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
for hwnd in windows:assert u.PostMessageW(hwnd,0x0010,0,0)
code=p.wait(timeout=30)
report={'exit_code':code,'pid':p.pid,'normal_window_close':True,'owned_windows':windows,'elapsed_seconds':time.time()-started,'log':str(o/'runtime.log'),'headset_operation':'unverified'}
(o/'process-result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert code==0
