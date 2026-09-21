from pathlib import Path
import json, zipfile, hashlib
R=Path(__file__).parent;O=R/'cglide'
src=O/'Room_108_INNOVATION_LAB.h3proj.zip'
im=R/'rooms/108/start_image_pilot/iLab_ImageGen_Start.png'
with zipfile.ZipFile(src) as z:
    p=json.loads(z.read('project.json'));readme=z.read('README.txt')
p['name']='iLab ImageGen first-frame pilot - visual test, registration unverified'
s=p['shots'][0]['state'];s['slots']['first']={'file':'ilab_imagegen_pilot_r11.png'}
s['prompt']=s['prompt'].replace('Eight fully clothed teenage students and one teacher: three students walk','Seven fully clothed teenage students and one teacher: two students walk')
p['shots'][0]['name']='108 - ImageGen start pilot (7 students + teacher)'
note='''Visual pilot only. Seven students and one teacher are visible. Main bench
and machine arrangement is broadly retained, but the generated image is not
pixel-exact to the Blender layout. Do not assume physical projection alignment.
No depth guide or static-camera LoRA is included in this H3 project.
This first-frame pilot has no additional reference images and no last frame.
Use the H3 FL2VA diffusion checkpoint specified in README.txt.
No H3 render has been submitted.\n'''
out=O/'Room_108_ImageGen_First_Frame_PILOT.h3proj.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED) as z:
    z.writestr('project.json',json.dumps(p,indent=2));z.writestr('README.txt',readme.decode()+note)
    z.write(im,'assets/ilab_imagegen_pilot_r11.png')
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert hashlib.sha256(z.read('assets/ilab_imagegen_pilot_r11.png')).digest()==hashlib.sha256(im.read_bytes()).digest()
(im.parent/'README.txt').write_text(note,encoding='ascii')
(im.parent/'H3_Pilot_Prompt.txt').write_text(s['prompt'].replace('@first','<Picture 1>'),encoding='ascii')
page=O/'index.html';text=page.read_text(encoding='utf-8')
if out.name not in text:
    text=text.replace('<table>',f'<p><a href="{out.name}" download>iLab ImageGen start-image PILOT</a> - separate visual test; seven students plus teacher, geometry not pixel-exact. <a href="../rooms/108/start_image_pilot/iLab_ImageGen_Start.png">Preview start image</a>.</p><table>')
page.write_text(text,encoding='utf-8')
print('Pilot packaged:',out)
