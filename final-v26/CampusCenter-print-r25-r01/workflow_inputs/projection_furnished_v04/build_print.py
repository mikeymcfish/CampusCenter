from pathlib import Path
import sys,json,hashlib,zipfile,time
R=Path(__file__).parent;sys.path.insert(0,str(R/'python_packages'));sys.path.insert(0,str(R.parent))
import numpy as np,trimesh,manifold3d as mf
from scipy.ndimage import maximum_filter
from print_heightfield_utils import write_stl
P=.5;S=.0875;O=np.array([-47,-2.3,-.42]);T=4.8
old=R.parent/'projection_print_v01/print_manifest.json';contract=json.loads(old.read_text())
SRC=Path(contract['source']);srcsha=hashlib.sha256(SRC.read_bytes()).hexdigest()
g=np.load(R.parent/'output_v12_roof_set/assembly_grids.npz')['ground']*4
g=np.repeat(np.repeat(g,2,0),2,1);ny,nx=g.shape;floor=(g>0)&(g<=T+.001)
d=np.load(R/'furniture_surfaces.npz');tri=(d['triangles'].astype(np.float64)-O)/S
mins=np.ceil(tri[:,:,:2].min(1)/P-.5).astype(int);maxs=np.floor(tri[:,:,:2].max(1)/P-.5).astype(int)
h=np.zeros(g.shape,np.float32);sampled=set()
for j,(v,lo,hi) in enumerate(zip(tri,mins,maxs)):
    x0,y0=np.maximum(lo,0);x1,y1=np.minimum(hi,[nx-1,ny-1])
    if x1<x0 or y1<y0:continue
    ax,ay=v[0,:2];bx,by=v[1,:2];cx,cy=v[2,:2];den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
    if abs(den)<1e-10:continue
    yy,xx=np.mgrid[y0:y1+1,x0:x1+1];px=(xx+.5)*P;py=(yy+.5)*P
    a=((by-cy)*(px-cx)+(cx-bx)*(py-cy))/den;b=((cy-ay)*(px-cx)+(ax-cx)*(py-cy))/den;c=1-a-b
    ok=(a>=-1e-6)&(b>=-1e-6)&(c>=-1e-6)&floor[y0:y1+1,x0:x1+1]
    z=a*v[0,2]+b*v[1,2]+c*v[2,2]
    ok&=(z>T+.6)&(z<50)
    if not ok.any():continue
    view=h[y0:y1+1,x0:x1+1];view[ok]=np.maximum(view[ok],z[ok]);sampled.add(int(d['owners'][j]))
    if j%50000==0:print('RASTER',j,flush=True)
# Reinforce fine backs/monitors by half a millimetre in plan. Every volume is
# filled straight down to the bed and later fused with the structural floor.
h=maximum_filter(h,size=3);h[~floor]=0;h=np.ceil(h/.2)*.2
for _ in range(10):
    a=h>0;d1=a[:-1,:-1]&a[1:,1:]&~a[:-1,1:]&~a[1:,:-1];d2=a[:-1,1:]&a[1:,:-1]&~a[:-1,:-1]&~a[1:,1:]
    if not(d1.any() or d2.any()):break
    yy,xx=np.where(d1);ok=floor[yy,xx+1];h[yy[ok],xx[ok]+1]=T
    yy,xx=np.where(d2);ok=floor[yy,xx];h[yy[ok],xx[ok]]=T
np.savez_compressed(R/'print_height_data.npz',furniture=h,structural_reference=g,pitch_mm=P)
write_stl(h,P,R/'supported_furniture_intermediate.stl')
def to_man(m):return mf.Manifold(mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def to_tri(m):
    a=m.to_mesh();return trimesh.Trimesh(np.asarray(a.vert_properties)[:,:3],np.asarray(a.tri_verts),process=True)
base=trimesh.load_mesh(SRC,process=True);base.apply_scale(4)
assert base.is_watertight and base.is_winding_consistent
basevol=base.volume;bm=to_man(base).simplify(.003);print('BASE_SIMPLIFIED',bm.num_tri(),flush=True)
furn=trimesh.load_mesh(R/'supported_furniture_intermediate.stl',process=True)
assert furn.is_watertight and furn.is_winding_consistent
fm=to_man(furn).simplify(.003);assert fm.status()==mf.Error.NoError
combined=(bm+fm).simplify(.003);assert combined.status()==mf.Error.NoError
mesh=to_tri(combined);assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1
assert np.allclose(mesh.bounds,base.bounds,atol=.02),(mesh.bounds,base.bounds)
down=mesh.face_normals[:,2]<-1e-5
elevated_down=down&(mesh.triangles_center[:,2]>.02)
assert not elevated_down.any(),int(elevated_down.sum())
full=R/'Campus_Center_Ground_Furnished_1_87p5.stl';mesh.export(full)
# Tile the same serialized surface used by the CAD and projection receivers.
combined=to_man(trimesh.load_mesh(full,process=True))
np.savez_compressed(R/'cad_mesh.npz',vertices=mesh.vertices,faces=mesh.faces)
print('FUSED',len(mesh.faces),mesh.volume,flush=True)
def three_mf(path,meshes):
    from xml.etree.ElementTree import Element,SubElement,tostring
    ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
    root=Element('model',{'unit':'millimeter','xml:lang':'en-US','xmlns':ns});res=SubElement(root,'resources');build=SubElement(root,'build')
    for i,(name,m,offset) in enumerate(meshes,1):
        ob=SubElement(res,'object',{'id':str(i),'type':'model','name':name});mo=SubElement(ob,'mesh');ve=SubElement(mo,'vertices');fa=SubElement(mo,'triangles')
        for v in m.vertices:SubElement(ve,'vertex',dict(zip(['x','y','z'],[f'{x:.6f}' for x in v])))
        for f in m.faces:SubElement(fa,'triangle',dict(zip(['v1','v2','v3'],[str(x) for x in f])))
        SubElement(build,'item',{'objectid':str(i),'transform':'1 0 0 0 1 0 0 0 1 '+' '.join(f'{x:.6f}' for x in offset)})
    types=b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels=b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('[Content_Types].xml',types);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',tostring(root,encoding='utf-8',xml_declaration=True))
out=R/'print_tiles';out.mkdir(exist_ok=True);rows=[];assembly=[];vol=0
xs=contract['split_x_mm'];ys=contract['split_y_mm']
for j in range(2):
    for i in range(3):
        lo=np.array([xs[i],ys[j],-1]);hi=np.array([xs[i+1],ys[j+1],60])
        cube=mf.Manifold.cube(tuple(hi-lo)).translate(tuple(lo))
        piece=to_tri(combined^cube);off=piece.bounds[0].copy();off[2]=0;piece.apply_translation(-off)
        assert piece.is_watertight and piece.is_winding_consistent and len(piece.split())==1
        assert not ((piece.face_normals[:,2]<-1e-5)&(piece.triangles_center[:,2]>.02)).any()
        assert np.all(piece.extents<=[290,300,315])
        name=f'Furnished_{chr(65+j)}{i+1}';p=out/(name+'.stl');piece.export(p)
        three_mf(out/(name+'.3mf'),[(name,piece,[0,0,0])]);vol+=piece.volume;assembly.append((name,piece,off))
        rows.append({'name':name,'file':p.name,'assembly_offset_mm':off.tolist(),'dimensions_mm':piece.extents.tolist(),'volume_mm3':float(piece.volume),'triangles':len(piece.faces),'single_component':True,'watertight':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        print('TILE',name,len(piece.faces),flush=True)
assert abs(vol-mesh.volume)/mesh.volume<1e-5
three_mf(R/'Campus_Center_Furnished_Assembly.3mf',assembly)
report={'status':'passed','structural_source':str(SRC),'structural_source_sha256':srcsha,'furniture_source':json.loads((R/'furniture_source.json').read_text())['source'],'scale':'1:87.5','assembly_bounds_mm':mesh.bounds.tolist(),'assembly_dimensions_mm':mesh.extents.tolist(),'floor_thickness_mm':4.8,'furniture_sampling_pitch_mm':P,'furniture_plan_reinforcement_mm':.5,'furniture_height_increment_mm':.2,'mesh_simplification_max_move_mm':.003,'furniture_mesh_parts_sampled':len(sampled),'furniture_raised_area_mm2':float((h>T+.1).sum()*P*P),'original_volume_mm3':basevol,'furnished_volume_mm3':float(mesh.volume),'added_volume_mm3':float(mesh.volume-basevol),'triangles':len(mesh.faces),'single_connected_solid':True,'watertight':True,'downward_faces_above_bed':int(elevated_down.sum()),'support_free_basis':'Furniture is vertically filled to bed; final union has no downward-facing faces above the flat underside. No overhead bridges or floating islands.','extra_ground_plane':False,'source_unchanged':hashlib.sha256(SRC.read_bytes()).hexdigest()==srcsha,'tiles_volume_relative_error':abs(vol-mesh.volume)/mesh.volume,'tiles':rows,'split_x_mm':xs,'split_y_mm':ys}
(R/'print_validation.json').write_text(json.dumps(report,indent=2));print('PRINT_COMPLETE',flush=True)
