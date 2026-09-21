"""Migrate active room prompts to first-frame H3; keep source refs for provenance."""
from pathlib import Path
import re, shutil
R=Path(__file__).parent
for p in sorted((R/'rooms').glob('*/H3_Loop_Prompt.txt')):
    old=p.read_text(encoding='utf-8')
    if old.startswith('For the target video'): continue
    backup=R/'revision_11_before'/p.relative_to(R)
    backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
    # Carry useful equipment descriptions into prose, without conditioning images.
    descriptions=[]
    for line in old.split('summary:')[0].splitlines():
        match=re.match(r'<Subject (\d+)>: <Picture \d+>\s+-\s+(.*)',line)
        if not match or int(match[1])<3:continue
        desc=match[2]
        desc=re.sub(r'Appearance only; Picture 1 controls scale and placement\.', '', desc)
        desc=re.sub(r'Picture 1 remains.*?authority\.', '', desc)
        desc=re.sub(r'Do not import.*?objects\.', '', desc)
        desc=desc.replace('Project render: furniture and King banners.', 'Furniture and King banners:')
        desc=desc.replace('from source PDF','').replace('Picture 1','the opening frame')
        descriptions.append(desc.strip())
    body=old.split('detailed_description:\n',1)[1].split('\n\noverall_soundscape:',1)[0]
    body=body[body.index('[Shot 1]'):]
    body=body.replace('References 2 onward supply surface and object appearance only; retain the overhead composition of <Subject 1> throughout.',
                      'Preserve the opening image composition and the people already visible in it. Animate their existing poses into the actions below; keep all visible architecture and furniture fixed.')
    body=body.replace('reference positions','opening positions').replace('reference footprint','opening footprint')
    appearance='Matte light-blue room walls, softly varied brick where already modeled, wood trim, green lounge upholstery and natural fabric clothing where those surfaces are present. Use these as subtle surface details, preserving the opening image shapes and colors.'
    text=('For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.\n\n'
          'integrated_multimodal_description: '+body+'\n'+appearance+'\n'+' '.join(descriptions)+
          '\n\noverall_soundscape: N/A\n\nnon_diegetic_music: N/A\n')
    assert text.isascii() and len(text)<7000
    assert '<Subject' not in text and '<Picture 2>' not in text
    p.write_text(text,encoding='utf-8',newline='\n')
print('31 prompts now use only the overhead first frame; appearance details retained in text.')
