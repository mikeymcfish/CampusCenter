from infinity_rooms_common import *
import zipfile,shutil,ast

mq=json.loads((D/'Mapped_Actual_Decode_And_Motion_QA.json').read_text());aq=json.loads((D/'Lossless_Atlas_Movie_QA.json').read_text());nq=json.loads((D/'Native_Fixed_Front_Reapplication_QA.json').read_text());gq=json.loads((C/'Infinity_Geometry_And_View_Contract.json').read_text());cq=json.loads((C/'Fixed_Front_Receiver_Cache_QA.json').read_text())
assert mq['status'].startswith('PASS') and aq['status'].startswith('PASS') and nq['status']=='PASS'
mq['visual_review_pending']=False;mq['all5_actual_decoded_and_native_keyframes_visually_reviewed']=True;write_json(D/'Mapped_Actual_Decode_And_Motion_QA.json',mq)
author=json.loads((D/'Mapped_Preview_And_Loop_QA.json').read_text());author['visual_review_pending']=False;author['native_Blender_validation_pending']=False;write_json(D/'Mapped_Preview_And_Loop_QA.json',author)
# The original reference test and accepted R04/H04 media remain unchanged.
preserved={
 'madmapper_production_P01/deliverables/Infinite_Floor/assembly_1_100/Infinite_Floor_P02_UV01_1_100_4096_HAP.mov':'6635c7d573bce9e373c10c1222400fb2edb72413f8c712046d802b4b89dec660',
 'madmapper_ripple_R04/whole_model/deliverables/Ripple_R04_Black_Thin_Staggered_Connected_UV02_1_100_4096_Lossless_PNG.mov':'615d32c42cddba4b7d4ce71a1c0168ed2d7db340a72ee490c32826bb5a225506',
 'madmapper_ripple_R04/whole_model/deliverables/Ripple_R04_Black_Thin_Staggered_Connected_44s_Mapped_1024_Lossless_Reference.mov':'3ba30a882ae941609e21e451998713df9d8c77392e975f71a743bb1e588a7116',
 'CampusCenter_UV02_H04_All13_30Pages_Bright_SameHue_CommonsFireplace_Tour_Test.zip':'2b83037a0af49bc25fdebae37f069d8b263cb9330718ffe44c75c239b8997916',
 'madmapper_highlight_H04_atlas_video_R01/CampusCenter_UV02_H04_All13_30Pages_300s_ATLAS_8192_Lossless_PNG.mov':'0006f47e7cd825836476c748a0ef234756ffe011d962588274310bce9e5ae538'}
for path,want in preserved.items():assert sha(R/path)==want,path
sp=json.loads((D/'Source_Preservation_QA.json').read_text());sp['additional_original_effect_and_accepted_media_SHA256_checks']=preserved;write_json(D/'Source_Preservation_QA.json',sp)
movies=[]
for role,q in [('compact fixed-front mapped viewing preview',mq),('lossless projection atlas',aq)]:
    p=D/q['file'];assert p.stat().st_size==q['bytes'] and sha(p)==q['sha256'];movies.append({'role':role,'file':q['file'],'bytes':q['bytes'],'sha256':q['sha256'],'duration_seconds':SECONDS,'fps':FPS,'frames':FRAMES})
manifest={'status':'PASS: Infinity Rooms R02 test ready for user review','movies':movies,'delivery_order':'Compact mapped MP4 first; actual atlas MOV next. The source package is supplemental.','receiver_OBJ':'Reference_Receiver/'+OBJ.name,'receiver_SHA256':sha(OBJ),'original_parts':['Opaque','Glazing','HangingLoops','Opaque_Fireplace_P03_B3'],'scale_denominator':100,'assembled_dimensions_mm':[657.6,512.0602094,46.872],'registration':'Frozen UV02 numeric model millimetres; shared world origin; +Z up, +Y north; original UV islands and model transformations unchanged.','viewpoint':{'eye_model_mm':EYE.tolist(),'target_model_mm':TARGET.tolist(),'horizontal_FOV_degrees':HFOV,'side_assumption':'South / negative Y, looking north; fixed front viewer. No earlier front-side decision was available.','physical_projector_pose_calibrated':False,'single_projector_assumed':True,'real_mesh_occlusion_retained':True,'hidden_surface_illumination_not_claimed':True},'visual_design':{'regions':len(gq['regions']),'scope':'Whole model eligible floor regions, including non-tour rooms; supports and architecture remain at their actual heights.','appearance':'Black background, cool contours on virtual recessed sidewalls, descending light planes and return; local region phases and shapes.','background_choice':'Chosen for this test to fit the accepted Ripple presentation; not stated as a user requirement for all future Infinity designs.','duration_seconds':SECONDS,'virtual_depth_minmax_model_mm':[min(x['maximum_virtual_depth_mm'] for x in gq['regions']),max(x['maximum_virtual_depth_mm'] for x in gq['regions'])],'physical_furniture':'Complete projected footprints protected with one-millimetre inflation and a stationary lip; all physical fixture atlas pixels are constant across all480 frames.','no_physical_geometry_motion':True,'regions_are_independent_apertures':'Existing open-area texture ownership boundaries create visual apertures only; they add no physical wall.','comfortable_motion_design':'One smooth descend/return per24s with deterministic staggered phases; no strobe, random flicker or added bloom.','loop':'Terminal virtual frame480 equals frame0 exactly; encoded frame479 is one normal time step before frame0.'},'QA':{'all480_mapped_and_atlas_frames_decode':True,'all480_atlas_PNG_packets_byte_identical_to_sources':True,'all5_actual_decoded_and_native_keyframes_visually_reviewed':True,'all_four_native_import_parts_vertices_UVs_and_identity_transforms_verified':True,'animated_aperture_overlap_full_furniture_and_walls_cells':0,'protected_source_files_unchanged':317,'current_accepted_Ripple_and_tour_media_unchanged':True,'largest_adjacent_source_frame_mean_RGB_byte_change':mq['largest_adjacent_source_frame_mean_absolute_RGB_byte_change'],'loop_wrap_mean_RGB_byte_change':mq['loop_wrap_mean_absolute_RGB_byte_change'],'physical_projection_and_MadMapper_runtime_tested':False},'boundary_limit':'Room identities and open-area divisions use inherited registered A101/H02/H03/H04 references intersected with actual physical domains and full print-mesh obstacle footprints. This is not a fresh R29 semantic perimeter audit.','required_user_test':'Assess the apparent depth from the assumed front side on the existing calibrated model; single-projector occlusion and transparent-window optical behaviour remain physical-test items.'}
write_json(D/'Infinity_Rooms_R02_Playback_And_View_Manifest.json',manifest)
readme='''CampusCenter UV02 Infinity Rooms R02 test

First open Infinity_Rooms_R02_WholeModel_UV02_24s_Fixed_Front_Mapped_1024_Viewing.mp4 to review the effect. It is a compact fixed-camera viewing reference.

For projection, use Infinity_Rooms_R02_WholeModel_UV02_24s_ATLAS_4096_Lossless_PNG.mov as the existing UV02 model's texture. It is the complete 4096 x 4096 UV atlas, 20 fps and 24 seconds. Its 480 original PNG packets are copied exactly. Keep the full square canvas and original UV02 receiver; use the existing calibration. The file does not create or modify any MadMapper project, cue or loop setting.

The model has 37 geometry-constrained visual apertures, including non-tour rooms. Cool light contours reveal virtual recessed sidewalls and independently phased descending/returning floors. Complete furniture, tabletop, bench, wall and corrected fireplace footprints stay on stationary protected supports. Their physical mesh and atlas pixels stay fixed. The depth is a colour illusion; the print remains unchanged.

The assumed viewer is at model XYZ (348.25,-600,850) mm, looking toward (348.25,252.875,12) mm, on the south/negative-Y front side. The perspective camera is fixed with 42-degree horizontal field of view. The actual projector pose was not supplied or calibrated. Real walls and fixtures retain their occlusions; one projector cannot be assumed to reach hidden surfaces. Evaluate the depth from this front-side assumption on the real setup.

Black is the chosen background for this test, following the accepted Ripple presentation. Each region completes a smooth 24-second descend/return with a deterministic phase offset. The virtual terminal frame equals frame0 exactly. The last encoded frame is one normal time step before the first. There is no flash, random flicker, noise, bloom or global grid pattern.

Reference_Receiver includes the unchanged four-part UV02 OBJ and MTL. Its SHA-256 is b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba. Model millimetres at1:100, shared world origin, +Z up and +Y north remain unchanged. The actual assembled dimensions are657.6 x512.0602094 x46.872mm. No sample1:250 compatibility is claimed.

QA verifies all480 frames decode, every atlas packet equals its source, exact timestamps, all37 aperture constraints, static fixture pixels, original native vertices/UVs/identity transforms, and all5 actual decoded/native keyframes. The review sheet columns are source mapped, decoded MP4, and fresh Blender; rows are0,6,12,18 and23.95seconds. The floor-aperture plan shows animated areas and protected furniture/supports. Existing open-area divisions are documented visual boundaries inherited from A101/H02/H03/H04; no fresh R29 semantic perimeter audit is claimed.

Physical projection, MadMapper runtime, projector calibration and transparent-window optical behaviour remain untested. The MP4 is lossy; the lossless atlas retains exact source pixels and black background. Original Blender, Unreal, print and MadMapper projects, the prior P01 floor test, accepted Ripple media and tour media remain unchanged.

Producer_Scripts records this authoring pipeline. Its Dependency_And_Input_Record.json identifies the existing producer-workspace inputs. The keyframe/receiver QA kit is not advertised as a standalone rebuild environment; the separate procedural source-backup work remains a later priority. The compact frozen aperture/depth input is included for audit and later reproduction. No full frame/state cache is included in this kit.
'''
(D/'README_Infinity_Rooms_R02.txt').write_text(readme,encoding='utf-8')
kit=T/'publisher_kit';kit.mkdir(exist_ok=True);ref=kit/'Reference_Receiver';ref.mkdir(exist_ok=True);shutil.copyfile(OBJ,ref/OBJ.name)
with OBJ.open(encoding='utf-8') as f:mtl_name=next(line.split(None,1)[1].strip() for line in f if line.startswith('mtllib '))
shutil.copyfile(OBJ.parent/mtl_name,ref/mtl_name)
shutil.copyfile(D/'Infinity_Rooms_R02_Frame_0000_Lossless_Atlas_4096.png',ref/'Atlas_Diagnostic.png')
for file in D.glob('*.json'):shutil.copyfile(file,kit/file.name)
for file in D.glob('*.png'):shutil.copyfile(file,kit/file.name)
shutil.copyfile(D/'README_Infinity_Rooms_R02.txt',kit/'README_Infinity_Rooms_R02.txt')
audit=kit/'Geometry_And_View_References';audit.mkdir(exist_ok=True)
for file in [C/'Infinity_Room_Apertures_And_Depth.npz',C/'Infinity_Geometry_And_View_Contract.json',C/'Fixed_Front_Receiver_Cache_QA.json']:shutil.copyfile(file,audit/file.name)
scripts=kit/'Producer_Scripts';scripts.mkdir(exist_ok=True)
files=['infinity_rooms_common.py','infinity_rooms_preflight.py','infinity_rooms_preview.py','infinity_rooms_native_preview.py','infinity_rooms_media_qa.py','infinity_rooms_finalize.py'];provenance=[]
for file in files:
    src=R/file;text=src.read_text();ast.parse(text)
    # Public provenance copies accept external FFmpeg executables through PATH.
    text=text.replace("os.environ.get('FFMPEG',r'T:\\AI\\ffmpeg\\bin\\ffmpeg.exe')","os.environ.get('FFMPEG','ffmpeg')")
    text=text.replace("('C:'+'/Users/')","('C:'+'/Users/')")
    ast.parse(text)
    (scripts/file).write_text(text,encoding='utf-8');provenance.append({'file':file,'production_SHA256':sha(src),'public_copy_SHA256':sha(scripts/file),'public_safe_path_and_literal_normalization_only':text!=src.read_text()})
inputs=[]
for p in [OBJ,R/'madmapper_ripple_R03/whole_model/Whole_Native_Obstacle_And_Ownership_Grid.npz',R/'madmapper_production_P01/navigation/obstacles.npy',R/'madmapper_production_P01/navigation/origin.npy',R/'madmapper_production_P01/navigation/Navigation_Contract.json',R/'madmapper_highlight_H03/world_clipped/deliverables/World_Clipped_Mask_Manifest.json',R/'print_revision02/deliverables/projection/Projection_Coordinate_Contract.json',R/'madmapper_hybrid_UV02/deliverables/Fireplace_New_Chart_Mask_8192.png',R/'madmapper_hybrid_UV02/deliverables/Fireplace_Only_Patch_8192.png',R/'madmapper_production_P01/cache/assembly_1_100_4096_world64/Cache_Contract.json']:
    inputs.append({'workspace_relative_path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'SHA256':sha(p),'in_kit':p==OBJ})
write_json(scripts/'Dependency_And_Input_Record.json',{'status':'Production provenance; standalone source-backup packaging is a separate pending priority','Python':'3.12.14','NumPy':'2.3.5','Pillow':'12.3.0','Blender':'5.0.0','FFmpeg':'2024-05-02-git-71669f2ad5 full_build','external_helper_modules':['production_common.py','production_navigation.py','uvprep_common.py'],'native_domain_inputs':'56 Connected_B*_Simulation_Domain.npz files from the accepted R03 physical domain audit; numerical union841555cells. Their complete source pipeline is being handled by the separate procedural rebuild backup.','existing_UV_cache_dependencies':'production_common build_cache reads the original UV01 receiver, Default_Opaque_Receiver_Mask.png, Projection_Coordinate_Contract.json and Usable_13_Stop_Copy.json. Cache is validated against the original UV01 receiver hash.','inputs':inputs,'scripts':provenance,'included_frozen_effect_input_SHA256':sha(C/'Infinity_Room_Apertures_And_Depth.npz'),'no_large_simulation_frame_or_state_caches_in_kit':True})
entries=sorted(p for p in kit.rglob('*') if p.is_file())
for p in entries:
    if p.suffix in ['.py','.txt','.json']:
        text=p.read_text(encoding='utf-8');assert 'C:\\Users\\' not in text and ('C:'+'/Users/') not in text and 'T:\\AI\\' not in text,p
fm=[{'file':p.relative_to(kit).as_posix(),'bytes':p.stat().st_size,'SHA256':sha(p)} for p in entries];write_json(kit/'File_SHA256_Manifest.json',{'files':fm})
archive=R/'CampusCenter_UV02_Infinity_Rooms_R02_Keyframes_Receiver_And_QA.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(kit.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(kit).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
handoff={'status':'PASS: current Infinity Rooms R02 test ready for sole publisher','parent_thread':'01a0f1b7-c8d5-710b-932e-bf37613d40f3','sole_publisher_thread':'01a0f763-261e-7288-bd51-e736fd8b50fe','delivery_order':'Compact mapped MP4 first, then actual lossless atlas MOV; supplemental QA kit.','movies':[{**q,'path':str((D/q['file']).resolve())} for q in movies],'QA_kit':{'path':str(archive.resolve()),'bytes':archive.stat().st_size,'SHA256':sha(archive)},'playback_manifest':str((D/'Infinity_Rooms_R02_Playback_And_View_Manifest.json').resolve()),'viewpoint_assumption':manifest['viewpoint'],'geometry_constrained_apertures':37,'animated_floor_texels':1027056,'all480frames_decode':True,'all480atlas_packets_exactly_match_source':True,'static_furniture_and_supports_all480frames':True,'all5_decoded_and_native_keyframes_reviewed':True,'original_geometry_UVs_scale_origin_and_prior_media_unchanged':True,'remaining_validation':'User visual review of this new test, physical projector calibration/MadMapper playback and assumed front-side optical effect remain untested.','public_rebuild_source_limit':'QA kit contains provenance scripts and input hashes, not a complete standalone producer environment; procedural-backup packaging remains lower priority.','GitHub_push_or_upload_performed':False,'new_Library_IDs':[]}
write_json(R/'INFINITY_ROOMS_R02_FINAL_PUBLISHER_HANDOFF.json',handoff)
first=json.loads((R/'INFINITY_ROOMS_R02_FIRST_MAPPED_PREVIEW_HANDOFF.json').read_text());first['atlas_movie_pending']=False;first['visual_review_complete']=True;first['final_publisher_handoff']=str((R/'INFINITY_ROOMS_R02_FINAL_PUBLISHER_HANDOFF.json').resolve());write_json(R/'INFINITY_ROOMS_R02_FIRST_MAPPED_PREVIEW_HANDOFF.json',first)
print(json.dumps(handoff,indent=2),flush=True)
