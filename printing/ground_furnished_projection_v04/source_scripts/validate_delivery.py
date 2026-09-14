from pathlib import Path
import sys,json,zipfile,hashlib,subprocess,xml.etree.ElementTree as ET
R=Path(__file__).parent;sys.path.insert(0,str(R/'python_packages'))
import numpy as np,trimesh
from PIL import Image
report={'status':'running','meshes':[],'three_mf':[],'videos':[]}
def checkmesh(m,name):
    assert m.is_watertight and m.is_winding_consistent,name
    components=len(m.split());assert components==1,(name,components)
    downward=(m.face_normals[:,2]<-1e-5)&(m.triangles_center[:,2]>.02)
    assert not downward.any(),(name,int(downward.sum()))
    return {'file':name,'watertight':True,'consistent_winding':True,'components':components,'elevated_downward_faces':0,'bounds_mm':m.bounds.tolist(),'volume_mm3':float(m.volume)}
full=trimesh.load_mesh(R/'Campus_Center_Ground_Furnished_1_87p5.stl',process=True)
report['meshes'].append(checkmesh(full,'Campus_Center_Ground_Furnished_1_87p5.stl'))
stls={}
for p in sorted((R/'print_tiles').glob('*.stl')):
    m=trimesh.load_mesh(p,process=True);stls[p.stem]=m;report['meshes'].append(checkmesh(m,p.name))
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
for p in [R/'Campus_Center_Furnished_Assembly.3mf',*sorted((R/'print_tiles').glob('*.3mf'))]:
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        root=ET.fromstring(z.read('3D/3dmodel.model'))
    assert root.attrib['unit']=='millimeter'
    meshes={};names={}
    for obj in root.findall('m:resources/m:object',ns):
        vv=np.array([[float(v.attrib[k]) for k in ['x','y','z']] for v in obj.findall('m:mesh/m:vertices/m:vertex',ns)])
        ff=np.array([[int(v.attrib[k]) for k in ['v1','v2','v3']] for v in obj.findall('m:mesh/m:triangles/m:triangle',ns)])
        m=trimesh.Trimesh(vv,ff,process=True);name=obj.attrib['name'];checkmesh(m,name)
        assert abs(m.volume-stls[name].volume)/m.volume<1e-6
        assert np.allclose(m.bounds,stls[name].bounds,atol=2e-6)
        meshes[obj.attrib['id']]=m;names[obj.attrib['id']]=name
    assembled=[]
    for item in root.findall('m:build/m:item',ns):
        a=np.array([float(x) for x in item.attrib['transform'].split()]);assert len(a)==12
        t=np.eye(4);t[:3,:3]=a[:9].reshape(3,3).T;t[:3,3]=a[9:]
        m=meshes[item.attrib['objectid']].copy();m.apply_transform(t);assembled.append(m)
    combined=trimesh.util.concatenate(assembled)
    if len(assembled)==6:
        assert np.allclose(combined.bounds,full.bounds,atol=3e-5)
        assert abs(combined.volume-full.volume)/full.volume<1e-5
    report['three_mf'].append({'file':p.name,'units':'millimeter','mesh_count':len(assembled),'STL_equivalence':True,'assembly_bounds_mm':combined.bounds.tolist()})
print('PRINT_REOPEN_VALIDATION_PASSED',flush=True)
pv=json.loads((R/'print_validation.json').read_text());fs=json.loads((R/'furniture_source.json').read_text())
for p,expected in [(pv['structural_source'],pv['structural_source_sha256']),(fs['source'],fs['source_sha256'])]:
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected,p
report['source_hashes_unchanged']=True
if '--print-only' not in sys.argv:
    info=R/'information';hs=json.loads((info/'render_hashes.json').read_text());ff='T:/AI/ffmpeg/bin/ffmpeg.exe';probe='T:/AI/ffmpeg/bin/ffprobe.exe'
    assert hs['master'][0]==hs['master'][-1] and hs['native'][0]==hs['native'][-1]
    report['first_last_frames_identical']=True
    for key,name,w,h,maskname in [('master','Campus_Center_Information_Master_RGB.mp4',2048,1572,'Projection_Validity.png'),('native','Campus_Center_Information_1024x786_RGB.mp4',1024,786,'Native_Validity.png')]:
        p=info/name;mask=np.array(Image.open(info/maskname).convert('L'))>127
        meta=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-of','json',str(p)]))['streams'][0]
        assert int(meta['width'])==w and int(meta['height'])==h and float(meta['duration'])==42 and int(meta['nb_frames'])==1008
        dec=subprocess.Popen([ff,'-v','error','-i',str(p),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
        count=0
        while True:
            buf=dec.stdout.read(w*h*3)
            if not buf:break
            assert len(buf)==w*h*3
            assert hashlib.sha256(buf).hexdigest()==hs[key][count],(key,count,'decode mismatch')
            arr=np.frombuffer(buf,np.uint8).reshape(h,w,3);assert not arr[~mask].any(),(key,count,'blackout violation')
            count+=1
            if count%240==0:print('DECODE_VERIFY',key,count,flush=True)
        assert dec.wait()==0 and count==1008
        report['videos'].append({'file':name,'resolution':[w,h],'frames':count,'seconds':42,'decoded_frames_match_source_hashes':True,'blackout_pixels_all_zero':True})
    for p in info.glob('*.png'):
        a=np.array(Image.open(p).convert('RGB'))
        if a.shape[:2]!=(1572,2048) or p.name=='Projection_Validity.png':continue
        mask=np.array(Image.open(info/'Projection_Validity.png').convert('L'))>127
        assert not a[~mask].any(),p.name
report['status']='passed';(R/('reopen_print_validation.json' if '--print-only' in sys.argv else 'delivery_validation.json')).write_text(json.dumps(report,indent=2))
print('DELIVERY_VALIDATION_PASSED',flush=True)
