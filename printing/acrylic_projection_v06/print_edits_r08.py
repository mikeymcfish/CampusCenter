"""Print-only subtraction: open iLab patio and six gym bleacher rows."""
from pathlib import Path
import json
import numpy as np

def regions(root):
    # Patio free edges sit west of Lab_west_wall; the north wall belongs to Aspire.
    # Stop at those two building faces. Preserve everything at/below the platform.
    lo=(np.array([-17500.,-500.])+[47000,2300])/87.5
    hi=(np.array([-11633.03664921466,6045.471204188481])+[47000,2300])/87.5
    result=[{'name':'Open innovation lab patio','lo':[*lo,4.8],'hi':[*hi,90.]}]
    objects=json.loads((root/'projection_furnished_v04/furniture_source.json').read_text())['objects']
    benches=[o for o in objects if 'bleacher' in o['name'].lower()]
    assert len(benches)==6
    for o in benches:
        b=np.array(o['bounds_m'])
        # Source furniture was rasterized at 0.5 mm and reinforced by one cell.
        # 0.85 mm covers rasterization/reinforcement without touching gym walls.
        xy=(b[:,:2]+[47,2.3])/.0875
        result.append({'name':o['name'],'lo':[*(xy[0]-.85),4.8],'hi':[*(xy[1]+.85),90.]})
    return result

def apply_edits(solid,root,out):
    import manifold3d as mf
    rows=regions(root);cuts=[]
    for r in rows:
        cuts.append(mf.Manifold.cube(tuple(np.array(r['hi'])-r['lo'])).translate(tuple(r['lo'])))
    cut=mf.Manifold.batch_boolean(cuts,mf.OpType.Add)
    volume_before=solid.volume();new=(solid-cut).simplify(.001)
    assert new.status()==mf.Error.NoError and new.volume()<volume_before
    assert (new^cut).volume()<.001
    (out/'r08_geometry_edits.json').write_text(json.dumps({'revision':'r08','regions':rows,'volume_before_mm3':volume_before,'volume_after_mm3':new.volume(),'removed_volume_mm3':volume_before-new.volume(),'bleacher_rows_removed':6,'patio_platform_preserved_below_mm':4.8,'print_only':True},indent=2))
    return new

def update_height_data(root,out):
    src=root/'projection_enclosed_v05/ground/print_height_data.npz'
    d=np.load(src);g=d['structural_reference'].copy();h=d['furniture'].copy();p=float(d['pitch_mm'])
    yy,xx=np.indices(g.shape);x=(xx+.5)*p;y=(yy+.5)*p
    for r in regions(root):
        lo=r['lo'];hi=r['hi'];mask=(x>=lo[0])&(x<=hi[0])&(y>=lo[1])&(y<=hi[1])
        g[mask]=np.minimum(g[mask],4.8);h[mask]=0
    np.savez_compressed(out/'print_height_data.npz',structural_reference=g,furniture=h,pitch_mm=p)
