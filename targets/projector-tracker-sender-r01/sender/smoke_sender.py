import os as _publication_os
def _publication_path(name, suffix):
 root=_publication_os.environ[name]
 return root.replace('\\','/').rstrip('/')+'/'+suffix

from pathlib import Path
import ctypes,subprocess,time,json,os,sys
from ctypes import wintypes
r=Path(__file__).resolve().parent
mode=sys.argv[1] if len(sys.argv)>1 else 'development'
b=Path(_publication_path('CC_REVIEW_ROOT', 'CampusCenter_ProjectorSender_R01/')+('ShippingQA' if mode.startswith('shipping') else 'Runtime')+'/Windows')
exe=b/'CampusCenter/Binaries/Win64/CampusCenter.exe'
log=r/('packaged-sender-'+mode+'-runtime.log')
args=[str(exe),'/Game/Campus/Maps/CampusCenter_Vive_R29_TrophyTrainerGymCorrections_r02','-DisablePlugins=MetaHumanCrowdContent','-EnablePlugins=OSC','-game','-nosplash','-windowed','-ResX=1280','-ResY=720','-CampusProjector','-ExecCmds=r.ScreenPercentage 50','-UserDir='+str(b/'SenderUserData')+'/', '-abslog='+str(log)]
if mode=='off':args=[a for a in args if a not in ['-CampusProjector','-EnablePlugins=OSC']]
p=subprocess.Popen(args,cwd=b)
k=ctypes.WinDLL('kernel32',use_last_error=True);u=ctypes.WinDLL('user32',use_last_error=True)
k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
k.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
h=k.OpenProcess(0x1000,False,p.pid);assert h
size=wintypes.DWORD(32768);buf=ctypes.create_unicode_buffer(size.value)
assert k.QueryFullProcessImageNameW(h,0,buf,ctypes.byref(size))
assert os.path.normcase(str(Path(buf.value).resolve()))==os.path.normcase(str(exe.resolve()))
windows=[];cb=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
u.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)];u.IsWindowVisible.argtypes=[wintypes.HWND]
def each(hwnd,param):
    pid=wintypes.DWORD();u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    if pid.value==p.pid and u.IsWindowVisible(hwnd):windows.append(int(hwnd))
    return True
u.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
time.sleep(15);assert p.poll() is None,p.returncode
u.EnumWindows(cb(each),0);assert windows,'No visible game window to test or close normally'
u.SetForegroundWindow.argtypes=[wintypes.HWND];u.GetForegroundWindow.restype=wintypes.HWND
foreground=[]
for hwnd in windows:
    result=bool(u.SetForegroundWindow(hwnd));foreground.append(dict(window=hwnd,activation_return=result,actual_foreground=int(u.GetForegroundWindow() or 0)))
    # A real client click gives the existing Slate game viewport keyboard focus.
    assert u.PostMessageW(hwnd,0x0201,1,(200<<16)|200)
    assert u.PostMessageW(hwnd,0x0202,0,(200<<16)|200)
# Scoped real desktop key events to this exact owned game window only. Enter the printed footprint.
for hwnd in windows:assert u.PostMessageW(hwnd,0x0100,0x57,0x00110001)
time.sleep(1.8)
for hwnd in windows:assert u.PostMessageW(hwnd,0x0101,0x57,0xC0110001)
for i in range(3):
    time.sleep(10);assert p.poll() is None,p.returncode;print('Owned sender game alive',flush=True)
for hwnd in windows:assert u.PostMessageW(hwnd,0x0010,0,0)
exit_code=p.wait(timeout=45)
text=log.read_text(errors='replace') if log.exists() else ''
errors=[line for line in text.splitlines() if any(s in line.lower() for s in ['fatal error','default material will be used','missing shader','failed to compile material'])]
report=dict(mode=mode,pid=p.pid,owned_native=str(exe),launch_args=args,exit=exit_code,normal_window_close=True,windows=windows,foreground=foreground,scoped_W_key_test=True,logging_available=bool(text),sender_started='CampusProjector: opt-in OSC v1' in text,map_loaded='CampusCenter_Vive_R29_TrophyTrainerGymCorrections_r02' in text,quest_overlay_mounted='CampusCenter-Quest3PCVRR01_2_P.utoc' in text,material_shader_fatal_errors=errors,headset_tested=False,source_geometry_recooked=False)
(r/('packaged-sender-'+mode+'-validation.json')).write_text(json.dumps(report,indent=2))
assert exit_code==0 and not errors,report
if mode=='off':assert not report['sender_started'] and report['map_loaded'],report
elif not mode.startswith('shipping'):assert report['sender_started'] and report['map_loaded'],report
print(json.dumps(report),flush=True)
