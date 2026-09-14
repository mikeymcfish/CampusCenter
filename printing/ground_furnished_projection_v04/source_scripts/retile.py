from pathlib import Path
import sys,json,zipfile,hashlib,ast
R=Path(__file__).parent;sys.path.insert(0,str(R/'python_packages'))
import numpy as np,trimesh,manifold3d as mf
# Reuse only the 3MF writer; do not execute the source rebuild.
tree=ast.parse((R/'build_print.py').read_text())
func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='three_mf')
exec(compile(ast.Module(body=[func],type_ignores=[]),'three_mf_writer','exec'))
full=trimesh.load_mesh(R/'Campus_Center_Ground_Furnished_1_87p5.stl',process=True)
solid=mf.Manifold(mf.Mesh(np.float32(full.vertices),np.uint32(full.faces)))
report=json.loads((R/'print_validation.json').read_text());xs=report['split_x_mm'];ys=report['split_y_mm'];rows=[];assembly=[]
for j in range(2):
    for i in range(3):
        lo=np.array([xs[i],ys[j],-1]);hi=np.array([xs[i+1],ys[j+1],60]);cut=solid^mf.Manifold.cube(tuple(hi-lo)).translate(tuple(lo));a=cut.to_mesh()
        m=trimesh.Trimesh(np.asarray(a.vert_properties)[:,:3],np.asarray(a.tri_verts),process=True);off=m.bounds[0].copy();off[2]=0;m.apply_translation(-off)
        assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
        assert not ((m.face_normals[:,2]<-1e-5)&(m.triangles_center[:,2]>.02)).any()
        name=f'Furnished_{chr(65+j)}{i+1}';p=R/'print_tiles'/(name+'.stl');m.export(p);three_mf(p.with_suffix('.3mf'),[(name,m,[0,0,0])]);assembly.append((name,m,off))
        rows.append({'name':name,'file':p.name,'assembly_offset_mm':off.tolist(),'dimensions_mm':m.extents.tolist(),'volume_mm3':float(m.volume),'triangles':len(m.faces),'single_component':True,'watertight':True,'elevated_downward_faces':0,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
three_mf(R/'Campus_Center_Furnished_Assembly.3mf',assembly)
report['tiles']=rows;report['tiles_volume_relative_error']=abs(sum(m.volume for _,m,_ in assembly)-full.volume)/full.volume
report['tile_cut_method']='Exact Boolean cuts without post-cut simplification; avoids seam overhang artifacts.'
assert report['tiles_volume_relative_error']<1e-6
(R/'print_validation.json').write_text(json.dumps(report,indent=2));print('EXACT_TILES_COMPLETE',report['tiles_volume_relative_error'])
