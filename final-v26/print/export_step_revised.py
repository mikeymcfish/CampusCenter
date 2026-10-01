from pathlib import Path
import sys,json,time
R=Path(__file__).parent;OLD=Path(r'C:\Users\mikef\Documents\ChatGPT\Campus Center');sys.path[:0]=[str(R/'python_packages'),str(OLD/'tmp/cadpackages')]
import numpy as np
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Sewing,BRepBuilderAPI_MakeSolid
from OCP.TopoDS import TopoDS,TopoDS_Compound
from OCP.TopAbs import TopAbs_SHELL,TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.STEPControl import STEPControl_Writer,STEPControl_Reader,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRep import BRep_Builder
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
for directory in sys.argv[1:]:
 D=R/directory;data=np.load(D/'cad_mesh.npz');v=data['vertices'];f=data['faces'];report=json.loads((D/'validation.json').read_text());sew=BRepBuilderAPI_Sewing(.0000001)
 for i,face in enumerate(f):
  t=v[face]
  if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))<1e-9:continue
  wire=BRepBuilderAPI_MakePolygon()
  for ix in face:wire.Add(gp_Pnt(*[float(x) for x in v[ix]]))
  wire.Close();sew.Add(BRepBuilderAPI_MakeFace(wire.Wire()).Face())
  if i%5000==0:print('CAD_FACES',directory,i,flush=True)
 sew.Perform();shells=[];shape=sew.SewedShape();e=TopExp_Explorer(shape,TopAbs_SHELL)
 if shape.ShapeType()==TopAbs_SHELL:shells=[TopoDS.Shell_s(shape)]
 else:
  while e.More():shells.append(TopoDS.Shell_s(e.Current()));e.Next()
 solids=[]
 for sh in shells:
  so=BRepBuilderAPI_MakeSolid(sh).Solid();assert BRepCheck_Analyzer(so).IsValid();unify=ShapeUpgrade_UnifySameDomain(so,True,True,True);unify.Build();solids.append(unify.Shape())
 assert len(solids)==report['components'],(directory,len(solids),report['components'])
 if len(solids)==1:shape=solids[0]
 else:
  shape=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(shape)
  for so in solids:builder.Add(shape,so)
 assert BRepCheck_Analyzer(shape).IsValid();p=GProp_GProps();BRepGProp.VolumeProperties_s(shape,p);expected=report['volume_mm3'];assert abs(p.Mass()-expected)/expected<1e-6
 name=next(D.glob('*.stl')).stem if directory=='stacked' else {'ground_furnished':'Ground_Furnished','ground_enclosed':'Ground_Enclosed','ground_acrylic':'Ground_Acrylic','upper_furnished':'Upper_Furnished','upper_enclosed':'Upper_Enclosed'}[directory]
 output=D/(name+'.step');w=STEPControl_Writer();assert w.Transfer(shape,STEPControl_AsIs)==IFSelect_RetDone;assert w.Write(str(output))==IFSelect_RetDone
 reader=STEPControl_Reader();assert reader.ReadFile(str(output))==IFSelect_RetDone;reader.TransferRoots();re=reader.OneShape();assert BRepCheck_Analyzer(re).IsValid();p2=GProp_GProps();BRepGProp.VolumeProperties_s(re,p2);assert abs(p2.Mass()-expected)/expected<1e-6
 e=TopExp_Explorer(re,TopAbs_SOLID);count=0
 while e.More():count+=1;e.Next()
 assert count==len(solids);bounds=Bnd_Box();BRepBndLib.Add_s(re,bounds);b=np.array(bounds.Get()).reshape(2,3);dims=b[1]-b[0];assert np.allclose(dims,report['dimensions_mm'],atol=.001)
 (D/'step_validation.json').write_text(json.dumps({'file':output.name,'valid_brep':True,'reopened_solid_count':count,'reopened_dimensions_mm':dims.tolist(),'reopened_volume_mm3':p2.Mass(),'mesh_volume_mm3':expected,'relative_volume_error':abs(p2.Mass()-expected)/expected,'representation':'Closed faceted B-representation, coplanar faces unified; editable generator and heightfield are supplied separately.'},indent=2));print('STEP_PASSED',directory,flush=True)
