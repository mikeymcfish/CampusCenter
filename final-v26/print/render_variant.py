import bpy,pathlib,json,math
from mathutils import Vector
R=pathlib.Path(__file__).parent;D=R/'review';D.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
sh=s.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_cavity=True;sh.cavity_type='BOTH';sh.show_shadows=True;sh.background_type='WORLD';s.world.color=(.92,.94,.96)
m=bpy.data.materials.new('Print solid');m.diffuse_color=(.72,.82,.88,1)
camdata=bpy.data.cameras.new('Print preview');cam=bpy.data.objects.new('Print preview',camdata);s.collection.objects.link(cam);s.camera=cam;camdata.type='ORTHO';camdata.clip_start=.001;camdata.clip_end=100
objects=[];records=[]
for folder,name in [('ground_furnished','Ground_Furnished'),('ground_enclosed','Ground_Enclosed'),('ground_acrylic','Ground_Acrylic'),('upper_enclosed','Upper_Enclosed')]:
 bpy.ops.wm.stl_import(filepath=str(R/folder/(name+'.stl')));o=bpy.context.object;o.name=name;o.scale=(.001,)*3;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);objects.append(o)
def render(name,visible,target=None,width=None,top=False):
 for o in objects:o.hide_render=o not in visible;o.hide_set(o not in visible)
 bpy.context.view_layer.update();points=[o.matrix_world@Vector(v) for o in visible for v in o.bound_box];lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)]);target=Vector(target) if target else (lo+hi)/2
 cam.location=target+(Vector((0,0,2)) if top else Vector((.75,-1,1.3)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=width or max(hi.x-lo.x,(hi.y-lo.y)*1.4)*1.2;s.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True);records.append({'image':name+'.png','objects':[o.name for o in visible],'target_m':list(target),'orthographic_width_m':camdata.ortho_scale})
ground=objects[0];upper=objects[3];render('ground_furniture_overview',[ground]);render('ground_furniture_top',[ground],top=True);render('upper_furniture_overview',[upper]);render('upper_furniture_top',[upper],top=True)
source=json.loads((R/'furniture_source.json').read_text());lookup={x['id']:x for x in source['groups']}
for stem,group,width in [('bleachers','PH_Gym_BleacherBank_01',.20),('locker_benches','PH14_G121_Bench_3',.14),('trainer','PH02_Trainer_046',.15)]:
 b=lookup[group]['source_item']['bounds_m'];target=(Vector(b[0])+Vector(b[1]))/2;target.x=(target.x+47)/87.5;target.y=(target.y+2.3)/87.5;target.z=.0048+target.z/87.5;render(stem,[ground],target,.0+width)
group=lookup['OriginalFitness_U218_Corrected'];b=group['source_item']['bounds_m'];target=(Vector(b[0])+Vector(b[1]))/2;target.x=(target.x+47)/87.5;target.y=(target.y+2.3)/87.5;target.z=.0048+(target.z-4.2672)/87.5;render('fitness_connected_overview',[upper],target,.25)
for stem,name in [('supported_rack_detail','RE07_PH02_Fitness218_010_0'),('standalone_bench_detail','RE07_PH02_Fitness218_035_0')]:
 # Exact view targets come from the pinned source mesh bounds.
 bounds=source['fitness_view_bounds'][name];target=(Vector(bounds[0])+Vector(bounds[1]))/2;target.x=(target.x+47)/87.5;target.y=(target.y+2.3)/87.5;target.z=.0048+(target.z-4.2672)/87.5;render(stem,[upper],target,.075)
stack=json.loads((R/'stacked_1_350/validation.json').read_text());so=[]
for level in ['ground','upper','roof']:
 bpy.ops.wm.stl_import(filepath=str(R/'stacked_1_350'/('Stack_'+level.title()+'.stl')));o=bpy.context.object;o.name='Stack_'+level.title();o.scale=(.001,)*3;o.location.z=stack['assembly_z_mm'][level]/1000;o.data.materials.append(m);objects.append(o);so.append(o)
render('miniature_assembled',so,width=.33)
for i,o in enumerate(so):o.location.z+=i*.035
render('miniature_separated',so,width=.38)
for i,o in enumerate(so):o.location.z-=i*.035
for o in objects:o.hide_render=o!=ground;o.hide_set(o!=ground)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'CampusCenter_Furniture_Print_Edit_R02.blend'))
(D/'render_receipt.json').write_text(json.dumps({'blender':bpy.app.version_string,'views':records,'geometry_source':'actual exported print STLs; no further geometry edits'},indent=2));print('RENDERED',len(records),flush=True)
