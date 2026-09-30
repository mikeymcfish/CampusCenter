"""Build a local review page showing the same rectangular masks as the decal materials."""
import html
import json
from pathlib import Path
root = Path(__file__).resolve().parent
manifest = json.loads((root/'manifest.json').read_text())
cards=[]
for art in manifest['artworks']:
    width,height=art['size_px']
    rects=''.join('<rect x="%s" y="%s" width="%s" height="%s"/>' % (r[0],r[1],r[2]-r[0],r[3]-r[1]) for r in [art['art_rect_px'],art['label_rect_px']])
    cards.append(f'''<figure><svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(art['student'])} artwork and name label"><defs><clipPath id="{art['id']}">{rects}</clipPath></defs><image href="{art['texture']}" width="{width}" height="{height}" clip-path="url(#{art['id']})"/></svg><figcaption><strong>{html.escape(art['student'])}</strong><span>{html.escape(art['title'])}</span></figcaption></figure>''')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Campus Center · Student art decals</title><style>*{box-sizing:border-box}body{margin:0;background:#f0eee8;color:#20313a;font:16px/1.5 system-ui,sans-serif}header,footer{max-width:1400px;margin:auto;padding:28px 36px}h1{margin:0;font-size:32px;font-weight:550}p{margin:8px 0}main{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;padding:24px 36px;background:#d6d6cd}figure{margin:0;min-width:0}svg{width:100%;height:410px;display:block}figcaption{padding:14px 12px;font-size:13px}figcaption strong,figcaption span{display:block}footer{font-size:14px}a{color:#204d72}@media(max-width:850px){main{grid-template-columns:repeat(2,minmax(0,1fr))}svg{height:340px}}@media(max-width:480px){main{grid-template-columns:1fr}} </style><header><p>KING SCHOOL · CAMPUS CENTER</p><h1>Student art for the commons hallway · v02</h1><p>Eight flat artwork adaptations with white student-name labels.</p></header><main>'''+''.join(cards)+'''</main><footer><p>Texture-and-mask preview, not an Unreal render. Imagegen adaptations of the credited reference photographs; fine details can differ from the originals.</p><p>Prepared for true projected decals. No artwork mesh, frame or backing geometry. Placement in Unreal is pending the Windows updater and visual review.</p><p><a href="README.md">PC instructions</a> · <a href="https://king-student-art-references.king-school-3694.chatgpt.site/">Reference archive</a></p></footer></html>'''
(root/'preview.html').write_text(page,encoding='utf-8')
