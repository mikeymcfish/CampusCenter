"""Reference-led architectural finish pass; run on Source_Copy.blend only."""
import bpy
import json
import math
import random
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).parent
random.seed(260922)
old = bpy.data.collections.get('Architect_Finishes_v01')
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
collection = bpy.data.collections.new('Architect_Finishes_v01')
bpy.context.scene.collection.children.link(collection)

def material(name, color, roughness=0.7):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    return m

blue = [material('AF_BlueTile_%02d' % i, c, .37) for i, c in enumerate([
    (.018,.065,.155), (.022,.074,.175), (.027,.083,.190), (.016,.059,.143)])]
oak = [material('AF_LightOak_%02d' % i, c, .52) for i, c in enumerate([
    (.43,.285,.145), (.47,.31,.165), (.45,.298,.158), (.49,.32,.175), (.42,.28,.145)])]
walnut = [material('AF_PerforatedWalnut_%02d' % i, c, .76) for i, c in enumerate([
    (.225,.135,.077), (.245,.151,.089), (.205,.123,.072)])]
white = material('AF_WarmWhitePlaster', (.81,.78,.71), .85)
cork = material('AF_NaturalCorkDisplay', (.34,.25,.17), .95)
navy = material('AF_KingBlueAccent', (.025,.135,.40), .5)
grid = material('AF_CeilingGridRecess', (.075,.065,.055), .9)
grout = material('AF_BlueTileGrout', (.21,.19,.16), .9)

def box(name, center, size, mat):
    verts=[(center[0]+x*size[0]/2,center[1]+y*size[1]/2,center[2]+z*size[2]/2)
           for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    collection.objects.link(o)
    o.data.materials.append(mat)
    return o

def tiled_surface(name, x0, x1, y0, y1, z, tile_x, tile_y, gap, mats, stagger):
    """One mesh, with real grout joints and stable per-face color variation."""
    verts, faces, mids = [], [], []
    row = 0
    y = y0
    while y < y1 - gap:
        xa = x0 - (tile_x / 2 if stagger and row % 2 else 0)
        while xa < x1 - gap:
            l, r = max(x0, xa) + gap / 2, min(x1, xa + tile_x) - gap / 2
            b, t = y + gap / 2, min(y1, y + tile_y) - gap / 2
            if r - l > .04 and t - b > .04:
                n = len(verts)
                verts.extend([(l,b,z),(r,b,z),(r,t,z),(l,t,z)])
                faces.append((n,n+1,n+2,n+3))
                mids.append(random.randrange(len(mats)))
            xa += tile_x
        y += tile_y
        row += 1
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for m in mats: mesh.materials.append(m)
    for p, mid in zip(mesh.polygons, mids): p.material_index = mid
    return obj

# Ground slab is one shared mesh, so shallow finish overlays keep every other room intact.
box('AF_CRI_BlueGroutBed', (8.16,7.69,.008), (16.0,13.98,.014), grout)
blue_floor = tiled_surface('AF_CRI_BlueTile_Staggered', .18,16.14,.70,14.68,.018,.47,.235,.005,blue,True)
def parquet_floor():
    verts,faces,uvs=[],[],[]
    # Paired perpendicular planks form a true repeating herringbone tessellation.
    width=.18; length=1.08; gap=.0018; angle=math.pi/4
    def rotate(x,y):return (8.18+(x-y)*math.cos(angle),22.76+(x+y)*math.sin(angle))
    def clip(poly,axis,limit,keepgreater):
        output=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            ai=(a[axis]>=limit) if keepgreater else (a[axis]<=limit)
            bi=(b[axis]>=limit) if keepgreater else (b[axis]<=limit)
            if ai:output.append(a)
            if ai!=bi:
                t=(limit-a[axis])/(b[axis]-a[axis]);output.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(4)))
        return output
    for i in range(-12,13):
      for j in range(-52,53):
       ox=i*length+j*width;oy=i*length-j*width
       for vertical in [False,True]:
        x0=ox+(length if vertical else 0)+gap/2;y0=oy+gap/2
        dx=(width if vertical else length)-gap;dy=(length if vertical else width)-gap
        poly=[]
        for u,v in [(0,0),(1,0),(1,1),(0,1)]:
            x,y=rotate(x0+u*dx,y0+v*dy);poly.append((x,y,v if vertical else u,u if vertical else v))
        for axis,limit,greater in [(0,.20,True),(0,16.16,False),(1,14.70,True),(1,30.82,False)]:
            poly=clip(poly,axis,limit,greater) if poly else []
        if len(poly)<3:continue
        n=len(verts);verts.extend((p[0],p[1],.023) for p in poly);faces.append(tuple(range(n,n+len(poly))));uvs.extend((p[2],p[3]*.18) for p in poly)
    mesh=bpy.data.meshes.new('AF_Herringbone');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('AF_Commons_Herringbone',mesh);collection.objects.link(obj)
    for mat in oak:mesh.materials.append(mat)
    uv=mesh.uv_layers.new(name='UVMap')
    for p in mesh.polygons:
        p.material_index=p.index%len(oak)
        for li in p.loop_indices:uv.data[li].uv=uvs[mesh.loops[li].vertex_index]
    return obj
box('AF_Commons_Parquet_JointBed',(8.18,22.76,.012),(15.96,16.12,.012),oak[0])
wood_floor=parquet_floor()

# West commons wall: warm low oak, white field, and irregular vertical timber/blue battens.
box('AF_Commons_West_OakWainscot', (.244,23.23,.635), (.035,13.45,1.27), oak[2])
box('AF_Commons_West_WhiteUpper', (.241,23.23,4.82), (.026,13.45,7.10), white)
# Segments measured from the architect image after perspective rectification.
measurements=json.loads((ROOT/'reference_batten_measurements.json').read_text())['segments']
for i,segment in enumerate(measurements):
    if segment['top']-segment['bottom'] < .055: continue
    if segment['color']=='blue' and .853<segment['x']<.962 and segment['top']<.70:continue
    y=16.55+segment['x']*13.42
    lo=1.42+segment['bottom']*6.85
    hi=1.42+segment['top']*6.85
    is_blue=segment['color']=='blue'
    width=min(.047 if is_blue else .072, max(.025,segment['width']*13.42*.72))
    box('AF_Reference_%s_%03d'%(segment['color'],i),(.29 if is_blue else .272,y,(lo+hi)/2),(.045,width,hi-lo),navy if is_blue else oak[i%5])

# Resolve highlights/occlusion in the measured K with smooth fitted endpoints.
for i in range(21):
    u=.85688+i*.005
    if u<.895:
        spans=[(.226-(u-.85688)*.23,.661-(u-.85688)*.77)]
    else:
        t=(u-.895)/(.95688-.895)
        spans=[(.39+.117*t,.475+.082*t),(.37-.17*t,.44-.167*t)]
    for j,(lo,hi) in enumerate(spans):
        box('AF_K_Fitted_%02d_%d'%(i,j),(.30,16.55+u*13.42,1.42+(lo+hi)*6.85/2),(.042,.043,(hi-lo)*6.85),navy)

# CRI display wall: oak dado and cork pin-up field with a narrow integrated rail.
box('AF_CRI_Display_OakDado', (.242,6.75,.625), (.036,11.30,1.25), oak[1])
box('AF_CRI_Display_Cork', (.242,6.75,1.90), (.030,11.30,1.30), cork)
box('AF_CRI_Display_TopRail', (.267,6.75,2.56), (.035,11.30,.026), oak[0])

# The existing six acoustic panels retain their placement and downlights.
for obj in bpy.data.objects:
    if obj.name.startswith('V5_Entry_acoustic_panel_') and obj.type == 'MESH':
        obj.data = obj.data.copy()
        obj.data.materials.clear()
        obj.data.materials.append(walnut[0])
        corners = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
        cx = (min(p.x for p in corners) + max(p.x for p in corners)) / 2
        cy = (min(p.y for p in corners) + max(p.y for p in corners)) / 2
        box('AF_CRI_WalnutPanel_' + obj.name.rsplit('_', 1)[-1],
            (cx, cy, 3.790), (1.97, 2.90, .008), walnut[0])
for x in [1,3,5,7,9,11,13]:
    box('AF_CRI_Grid_X_%02d' % x, (x,12.10,3.786), (.015,2.90,.012), grid)
for j, y in enumerate([10.65,11.375,12.10,12.825,13.55]):
    box('AF_CRI_Grid_Y_%02d' % j, (7.0,y,3.786), (12.0,.015,.012), grid)

# Open linear canopy: timber fins turn from the feature wall onto a pale soffit.
box('AF_Commons_PaleCeiling', (6.10,22.95,8.386), (12.05,16.70,.018), white)
for i in range(124):
    y = 14.65 + i * .134
    x0=.18; j=0
    while x0<12.05:
        length = min(random.uniform(.55,1.65),12.10-x0)
        box('AF_Canopy_%02d_%d' % (i,j), (x0+length/2,y,8.23),
            (length,.036,.045), navy if (i*3+j*5)%29==0 else oak[(i+j)%5])
        x0+=length+random.uniform(.07,.19);j+=1
for i in range(13):
    box('AF_Canopy_CrossRail_%02d'%i, (.22+i*.96,22.95,8.31), (.025,16.70,.035), oak[0])

# Save only the isolated copy; furniture, people, and fixtures are not edited.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Campus_Center_Architect_Finishes_v01.blend'))
report = {
    'source': 'output_v18/Campus_Center_Textured.blend',
    'blend': 'Campus_Center_Architect_Finishes_v01.blend',
    'added_objects': len(collection.objects),
    'blue_tile_faces': len(blue_floor.data.polygons),
    'oak_floor_faces': len(wood_floor.data.polygons),
    'scope': 'Commons and CRI walls, ceilings and floor only',
}
(ROOT / 'build_report.json').write_text(json.dumps(report, indent=2))
print('FINISHES_SAVED', report)
