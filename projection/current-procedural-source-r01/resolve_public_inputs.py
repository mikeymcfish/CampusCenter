"""Resolve frozen published receivers; never substitutes a different revision."""
from pathlib import Path
import argparse,hashlib,json,shutil,urllib.request,zipfile
R=Path(__file__).parent
COMMIT='74081e3fb86e879085c371853f66fc34f70053a6'
UV01_REL='projection/p02-madmapper-uv01/assembly_1_100/CampusCenter_P02_Assembly_1_100_UV01.obj'
UV01_URL='https://raw.githubusercontent.com/mikeymcfish/CampusCenter/'+COMMIT+'/'+UV01_REL
ZIP_URL='https://github.com/mikeymcfish/CampusCenter/releases/download/campuscenter-ripple-r04-black-thin-staggered-atlas-20261006/CampusCenter_UV02_Ripple_R04_Keyframes_Receiver_and_QA.zip'
ZIP_SHA='a44a71da3c9d080978d7404b0141aea6e8679e04a09f072458cacf6d0accd97d'
UV01_SHA='5fb3d64faebe846255f84b4e4f2be832070fec649ea99a1005d69f0c802db45f'
UV02_SHA='b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba'
MTL_SHA='8f71eea8b37df7d0705cdfa9f69afde3d0fbde5cd8e524e04ae4b4f88de3c715'
TARGET01=R/'madmapper_p02/deliverables/assembly_1_100'/Path(UV01_REL).name
TARGET02=R/'madmapper_hybrid_UV02/deliverables/CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj'
TARGET_MTL=TARGET02.parent/'CampusCenter_P02_Assembly_1_100_UV01.mtl'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def download(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(url,timeout=45) as response,path.open('xb') as out:
        while data:=response.read(1024*1024):out.write(data)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path);ap.add_argument('--receiver-zip',type=Path);ap.add_argument('--download',action='store_true');a=ap.parse_args();receipt=[]
    if not TARGET01.exists():
        TARGET01.parent.mkdir(parents=True,exist_ok=True)
        if a.repo:shutil.copyfile(a.repo/UV01_REL,TARGET01)
        elif a.download:download(UV01_URL,TARGET01)
        else:raise SystemExit('UV01 missing: use --repo with the frozen checkout or --download.')
    assert sha(TARGET01)==UV01_SHA,'UV01 receiver hash mismatch; refusing substitute'
    if not TARGET02.exists() or not TARGET_MTL.exists():
        archive=a.receiver_zip
        if archive is None:
            archive=R/'.download_cache/Published_R04_Receiver_QA.zip'
            if not archive.exists():
                if not a.download:raise SystemExit('UV02 missing: provide --receiver-zip or --download.')
                download(ZIP_URL,archive)
        assert sha(archive)==ZIP_SHA,'Published receiver archive hash mismatch'
        with zipfile.ZipFile(archive) as z:
            for file in ['CampusCenter_P02plusP03B3_Assembly_1_100_UV02.obj','CampusCenter_P02_Assembly_1_100_UV01.mtl']:
                matches=[n for n in z.namelist() if n.endswith('/'+file)];assert len(matches)==1,(file,matches)
                target=TARGET02.parent/file;target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists():
                    with target.open('xb') as f:f.write(z.read(matches[0]))
    assert sha(TARGET02)==UV02_SHA,'UV02 receiver hash mismatch; refusing substitute'
    assert sha(TARGET_MTL)==MTL_SHA,'UV02 receiver MTL hash mismatch; refusing substitute'
    for p,h,url in [(TARGET01,UV01_SHA,UV01_URL),(TARGET02,UV02_SHA,ZIP_URL),(TARGET_MTL,MTL_SHA,ZIP_URL)]:receipt.append({'file':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'expected_sha256':h,'verified':True,'published_source':url})
    (R/'Resolved_Public_Inputs_QA.json').write_text(json.dumps({'status':'PASS','commit':COMMIT,'receivers':receipt,'native_actor_inputs':'Included separately in this new source bundle; absent from prior public media kits.'},indent=2));print(json.dumps({'status':'PASS: exact published UV01 and UV02 receivers resolved','receivers':receipt},indent=2))
if __name__=='__main__':main()
