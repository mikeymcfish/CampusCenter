from pathlib import Path
import sys,json,time
R=Path(__file__).parent/'print';sys.path.insert(0,str(R.parent.parent/'tmp/cadpackages'))
import numpy as np
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Sewing,BRepBuilderAPI_MakeSolid
from OCP.TopoDS import TopoDS
from OCP.TopAbs import TopAbs_SHELL,TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.STEPControl import STEPControl_Writer,STEPControl_Reader,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
data=np.load(R/'cad_mesh.npz');v=data['vertices'];f=data['faces']
sew=BRepBuilderAPI_Sewing(.0001)
for i,face in enumerate(f):
    wire=BRepBuilderAPI_MakePolygon()
    for ix in face:wire.Add(gp_Pnt(*[float(x) for x in v[ix]]))
    wire.Close();sew.Add(BRepBuilderAPI_MakeFace(wire.Wire()).Face())
    if i%5000==0:print('CAD_FACES',i,flush=True)
sew.Perform();shells=[];e=TopExp_Explorer(sew.SewedShape(),TopAbs_SHELL)
if sew.SewedShape().ShapeType()==TopAbs_SHELL:shells=[TopoDS.Shell_s(sew.SewedShape())]
else:
    while e.More():shells.append(TopoDS.Shell_s(e.Current()));e.Next()
assert len(shells)==1,len(shells)
shape=BRepBuilderAPI_MakeSolid(shells[0]).Solid();assert BRepCheck_Analyzer(shape).IsValid()
unify=ShapeUpgrade_UnifySameDomain(shape,True,True,True);unify.Build();shape=unify.Shape()
assert BRepCheck_Analyzer(shape).IsValid()
p=GProp_GProps();BRepGProp.VolumeProperties_s(shape,p);volume=p.Mass()
expected=json.loads((R/'print_validation.json').read_text())['furnished_volume_mm3'];assert abs(volume-expected)/expected<1e-6
out=R/'Campus_Center_Ground_Acrylic_1_87p5.step';w=STEPControl_Writer();assert w.Transfer(shape,STEPControl_AsIs)==IFSelect_RetDone;assert w.Write(str(out))==IFSelect_RetDone
reader=STEPControl_Reader();assert reader.ReadFile(str(out))==IFSelect_RetDone;reader.TransferRoots();s=reader.OneShape();assert BRepCheck_Analyzer(s).IsValid()
e=TopExp_Explorer(s,TopAbs_SOLID);count=0
while e.More():count+=1;e.Next()
assert count==1,count
p2=GProp_GProps();BRepGProp.VolumeProperties_s(s,p2);assert abs(p2.Mass()-expected)/expected<1e-6
(R/'cad_validation.json').write_text(json.dumps({'status':'passed','file':out.name,'units':'millimetres','scale':'1:87.5','solid_count':count,'valid_brep':True,'reopened_volume_mm3':p2.Mass(),'mesh_volume_mm3':expected,'relative_volume_error':abs(p2.Mass()-expected)/expected,'representation':'Closed faceted B-representation, coplanar faces unified. Exact supported print solid; no original parametric feature history.'},indent=2))
print('CAD_COMPLETE',volume,flush=True)
