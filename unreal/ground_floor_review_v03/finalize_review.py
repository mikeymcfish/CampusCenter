"""Summarize four independent reports without altering their scores."""
from pathlib import Path
import json
R=Path(__file__).parent
reviews=[json.loads((R/f'critic_round_{i}'/'review.json').read_text()) for i in range(1,5)]
for r in reviews:r['scores']=r.get('scores') or {k:r[k] for k in ['design','aesthetics','accuracy','overall']}
validation=json.loads((R/'delivery_validation.json').read_text())
assert not validation['errors']
assert all(len(r['zone_scores'])==31 for r in reviews)
counts=[]
for i,r in enumerate(reviews,1):
    manifest=json.loads((R/f'critic_round_{i}'/'coverage_manifest.json').read_text(encoding='utf-8-sig'))
    complete=json.loads((R/f'critic_round_{i}'/'capture_complete.json').read_text())
    assert not complete['missing']
    assert all((R/f'critic_round_{i}'/(v['name']+'.png')).is_file() for v in manifest['views'])
    counts.append(len(manifest['views']))
final=reviews[-1]
passed=final['scores']['overall']>=8.5 and final['zero_visible_errors']
scores=[r['scores']['overall'] for r in reviews]
summary={'rounds':4,'zones':31,'base_images_per_round':counts,'scores':scores,'final_scores':final['scores'],'visual_gate_passed':passed,'zero_visible_errors':final['zero_visible_errors'],'saved_map_validation_errors':validation['errors'],'map':validation['map'],'artworks':validation['artworks'],'trophies':validation['trophies'],'runtime_performance_measured':False}
(R/'summary.json').write_text(json.dumps(summary,indent=2))
result='met' if passed else '**not met**'
header=f'''## Ground-floor review — September 25, 2026

The current launchers open `{validation['map']}` in Unreal Engine 5.8.2. This is the current editable walkthrough revision; sections below describe historical revisions.

**Four new independent critic rounds covered 31 ground-floor rooms/zones and {sum(counts)} base screenshots**, plus camera-repair evidence. Scores: **{' → '.join(f'{s:.1f}' for s in scores)}/10**. The requested 8.5/10 and zero-visible-errors gate was {result}. See the final critic report for remaining defects and scope limitations.

[Offline review gallery](ground_floor_review_v03/review_gallery.html) | [Final critic report](ground_floor_review_v03/critic_round_4/review.md) | [Scope and changes](ground_floor_review_v03/README.md) | [Saved-map validation](ground_floor_review_v03/delivery_validation.json)

The passes improved ground-floor lighting, floor continuity, architectural material scale and grout, and removed an exterior tree intrusion from the gym. Existing furniture, the K-wall geometry, all nine artwork decals and ten trophy decals are preserved. The prior maps and Blender master are unchanged. The gym finish is inferred; exact architect-pattern matching throughout the building is not established.

Saved-map validation found zero structural preservation/dependency errors across 1,013 existing mesh actors. This does **not** mean the visual zero-error gate passed. `GROUND_FLOOR_ASSET_MANIFEST.json` records delivery hashes. Higher shadow quality is enabled; performance was not remeasured. The legacy standalone executable was not rebuilt.

Run `git lfs pull` after cloning, then `Launch_Unreal.cmd` to walk or `Edit_Commons_Dusk.cmd` to edit. Open the gallery locally after pulling LFS assets.

---
'''
(R/'repo_header.md').write_text(header,encoding='utf-8')
print(json.dumps(summary,indent=2))
