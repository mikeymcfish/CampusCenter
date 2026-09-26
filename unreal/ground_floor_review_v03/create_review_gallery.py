"""Build a local, offline gallery from the independent critic's actual evidence."""
from pathlib import Path
import json,html
R=Path(__file__).parent
reviews=[]
for i in range(1,5):
    folder=R/f'critic_round_{i}'
    review=json.loads((folder/'review.json').read_text())
    manifest=json.loads((folder/'coverage_manifest.json').read_text(encoding='utf-8-sig'))
    views=[]
    for v in manifest['views']:
        p=folder/(v['name']+'.png');assert p.is_file(),p
        views.append({'zone':v['zone'],'name':v['name'],'url':p.relative_to(R).as_posix()})
    repairs=R/f'critic_round_{i}_repairs'
    if (repairs/'coverage_manifest.json').is_file():
        for v in json.loads((repairs/'coverage_manifest.json').read_text(encoding='utf-8-sig'))['views']:
            p=repairs/(v['name']+'.png')
            if p.is_file():views.append({'zone':v['zone'],'name':v['name']+' (camera repair)','url':p.relative_to(R).as_posix()})
    scores=review.get('scores') or {k:review[k] for k in ['design','aesthetics','accuracy','overall']}
    reviews.append({'round':i,'scores':scores,'zones':review['zone_scores'],'views':views,'report':f'critic_round_{i}/review.md'})
data=json.dumps(reviews).replace('</','<\\/')
doc='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Campus Center · Ground floor review</title><style>
*{box-sizing:border-box}body{margin:0;background:#111b29;color:#ebedf0;font:15px/1.5 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:40px 28px}h1{font-size:36px;line-height:1.1;margin:10px 0 16px}h2{font-size:24px}.eyebrow{color:#cfb784;text-transform:uppercase;letter-spacing:.14em;font-size:12px}.muted{color:#aab7c8;max-width:920px}a{color:#a4cfff}.scores{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:28px 0}.score{padding:18px;background:#1c2b40;border:1px solid #31435b;border-radius:8px}.score b{display:block;font-size:32px}.controls{display:flex;gap:16px;align-items:center;flex-wrap:wrap}select{background:#1c2b40;color:white;border:1px solid #63758c;border-radius:5px;padding:9px;font:inherit}.images{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:24px 0}figure{margin:0;background:#1c2b40;border-radius:6px;overflow:hidden}img{width:100%;display:block}figcaption{padding:10px;color:#c8d3e2}table{border-collapse:collapse;width:100%;margin-top:24px}th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #31435b}th{color:#aab7c8}tbody tr{cursor:pointer}tbody tr:hover{background:#22354d}.finding{padding:16px;background:#1c2b40;border-left:3px solid #cfb784;margin:18px 0}@media(max-width:800px){.images{grid-template-columns:1fr}.scores{grid-template-columns:repeat(2,1fr)}main{padding:24px 14px}h1{font-size:28px}}
</style><main><div class="eyebrow">Campus Center / Unreal walkthrough</div><h1>Four rounds · Entire ground floor</h1><p class="muted">Independent art-direction review of 31 scheduled rooms and zones, with wide views, details and ground-level staircase approaches. Target: at least 8.5/10 and zero visible errors. Existing furniture and all 19 supplied artwork/trophy decals are preserved.</p><div id="scores" class="scores"></div><p class="muted">Some camera positions were corrected between rounds. Camera repairs are included below; images are unretouched engine captures. Scores describe visual presentation, not measured frame rate or gameplay testing.</p><h2>Inspect the evidence</h2><div class="controls"><label>Round <select id="round"></select></label><label>Room <select id="zone"></select></label><a id="report">Full critic report</a></div><div id="finding" class="finding"></div><div id="images" class="images"></div><h2>Every ground-floor zone</h2><p class="muted">Select a row to inspect its screenshots. Fitness and upper balconies are upstairs and excluded.</p><table><thead><tr><th>Room / zone</th><th>Round 1</th><th>Round 2</th><th>Round 3</th><th>Round 4</th></tr></thead><tbody id="matrix"></tbody></table></main><script>
const data=DATA;const el=id=>document.getElementById(id);const zoneRows=data[3].zones;
for(const d of data){const card=document.createElement('div');card.className='score';card.textContent='Round '+d.round;const b=document.createElement('b');b.textContent=d.scores.overall.toFixed(1)+' / 10';card.append(b);el('scores').append(card);el('round').add(new Option('Round '+d.round,d.round-1));}
el('round').value=3;for(const z of zoneRows)el('zone').add(new Option(z.id+' · '+z.name,z.id));
function render(){const d=data[+el('round').value],id=el('zone').value,z=d.zones.find(z=>z.id===id);el('finding').textContent=z?z.overall+'/10 · '+z.finding:'';el('report').href=d.report;el('images').replaceChildren();for(const v of d.views.filter(v=>v.zone===id)){const f=document.createElement('figure'),a=document.createElement('a'),img=document.createElement('img'),c=document.createElement('figcaption');a.href=v.url;a.target='_blank';img.src=v.url;img.alt=v.name;img.loading='lazy';a.append(img);c.textContent=v.name;f.append(a,c);el('images').append(f);}}
for(const z of zoneRows){const tr=document.createElement('tr'),td=document.createElement('td');td.textContent=z.id+' · '+z.name;tr.append(td);for(const d of data){const cell=document.createElement('td'),v=d.zones.find(v=>v.id===z.id);cell.textContent=v?v.overall.toFixed(1):'—';tr.append(cell);}tr.onclick=()=>{el('zone').value=z.id;render();el('finding').scrollIntoView({behavior:'smooth',block:'start'});};el('matrix').append(tr);}
el('zone').onchange=render;el('round').onchange=render;render();
</script></html>'''.replace('DATA',data)
(R/'review_gallery.html').write_text(doc,encoding='utf-8')
print('Built review_gallery.html with',sum(len(r['views']) for r in reviews),'verified screenshots')
