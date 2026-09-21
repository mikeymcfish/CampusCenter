"""Strengthen static projection framing without changing reference roles or assets."""
from pathlib import Path
import shutil

root = Path(__file__).parent
backup = root / 'revision_10_before'
count = 0
for p in sorted((root / 'rooms').glob('*/H3_Loop_Prompt.txt')):
    text = p.read_text(encoding='utf-8')
    if 'Every stationary landmark occupies' in text:
        continue
    dest = backup / p.relative_to(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    text = text.replace('Cinematic appearance guide', 'Material and clothing appearance reference')
    text = text.replace('A photorealistic 12-second seamless overhead projection loop',
                        'A static-camera 12-second seamless overhead projection loop')
    text = text.replace('Locked vertical orthographic architectural photography, square framing, every receiving surface sharply focused. Soft fixed illumination and grounded contact shadows. Fine natural material variation, realistic anatomy and subtle fabric movement. No cinematic lens perspective or depth of field from the appearance references.',
                        'Photographic materials and natural human movement in a fixed orthographic floor-plan view. Uniform sharp focus, steady illumination and grounded contact shadows.')
    text = text.replace('[Shot 1] One continuous 12-second shot.',
        '[Shot 1] Static Shot for the entire 12 seconds. The camera is rigidly fixed directly above the room, looking vertically down, with constant position, orientation and orthographic scale. Every stationary landmark occupies the SAME screen coordinates in EVERY frame: room corners, door thresholds, bench ends and the black mask edge. Keep the complete room silhouette and black margins identical from start to finish. Only people animate inside this stationary background; their movement never causes the camera to follow or reframe. No pan, tilt, orbit, zoom, dolly, drift or parallax. References 2 onward supply surface and object appearance only; retain the overhead composition of <Subject 1> throughout.')
    assert text.isascii() and len(text) < 6990, (p, len(text))
    assert text.count('[Shot 1]') == 1
    p.write_text(text, encoding='utf-8', newline='\n')
    count += 1
print(f'Updated {count} room prompts; originals preserved in {backup}')
