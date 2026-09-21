from pathlib import Path
import sys,json,time,traceback
R=Path(__file__).resolve().parent
trial=sys.argv[1] if len(sys.argv)>1 else 'ltx_endpoints'
sys.path[:0]=[str(R/'python_deps'),'T:/AI/Wan2GP']
from shared.api import init
out=R/'trials'/trial;out.mkdir(parents=True,exist_ok=True)
class Events:
    def on_event(self,event):
        if event.kind=='preview':return
        with (out/'events.log').open('a',encoding='utf-8') as f:f.write(str(event.kind)+' '+str(event.data)+'\n')
(out/'status.json').write_text(json.dumps({'status':'initializing','started':time.time()}))
try:
    session=init(root='T:/AI/Wan2GP',output_dir=str(out),console_output=True,callbacks=Events())
    model='minimax_h3_fl2va' if trial.startswith('h3') else 'ltx2_22B_distilled_1_1'
    settings=session.get_default_settings(model)
    frame=R.parent/'projection_acrylic_v06/rooms/108/start_image_pilot/iLab_ImageGen_Start.png'
    prompt=('Locked static straight-down orthographic view of the innovation lab shown in the opening image. '
      'Seven fully clothed students and one teacher remain the same people. The two students in the open aisles take a few natural steps around short closed paths and return to their starting poses. '
      'Four students at the right-hand worktables make subtle repeated hand gestures; the student beside the printers watches and the teacher gestures gently. '
      'All room corners, table edges, machines, chairs and black margins stay at exactly the same screen coordinates throughout. Only people move. '
      'The camera never pans, tilts, zooms, rotates or follows a person. Fixed illumination. No new furniture or people. '
      'End on the supplied identical last frame, smoothly matching opening positions. Silent output.')
    frames=107 if model.startswith('minimax') else 105
    if model.startswith('minimax'):
        prompt=('How the reference pictures align with the target video - Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 4.46-second mark of the target video.\n\nintegrated_multimodal_description: [Shot 1] '+prompt+'\n\noverall_soundscape: N/A\n\nnon_diegetic_music: N/A')
    settings.update(model_type=model,prompt=prompt,prompt_enhancer='',image_start=str(frame),image_end=str(frame),image_prompt_type='',resolution='512x512',video_length=frames,seed=42621,repeat_generation=1,batch_size=1,force_fps='24',audio_prompt_type='',spatial_upsampling='',temporal_upsampling='',multi_prompts_gen_type='FG')
    if model.startswith('minimax'):settings['override_profile']=5
    if trial.startswith('ltx_depth'):
        settings.update(video_prompt_type='VG',video_guide=str(R/'depth/108/Depth_Guide_105f.mp4'),activated_loras=['T:/AI/Wan2GP/loras/ltx2_22B/ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors'],loras_multipliers='0.7',control_net_weight=0.7)
        if trial=='ltx_depth_moving':settings.update(video_guide=str(R/'depth/108/moving/Blender_Moving_Depth.mp4'),loras_multipliers='0.7',prompt=prompt+' The depth guide shows the intended walking movement. Follow the two moving people while all equipment stays fixed.')
    (out/'settings.json').write_text(json.dumps(settings,indent=2,default=str))
    (out/'status.json').write_text(json.dumps({'status':'running','model':model,'started':time.time()}))
    t=time.monotonic();result=session.run_task(settings)
    report={'status':'finished' if not result.errors else 'failed','seconds':time.monotonic()-t,'generated_files':result.generated_files,'errors':[str(e) for e in result.errors]}
    (out/'status.json').write_text(json.dumps(report,indent=2,default=str));print(json.dumps(report,default=str),flush=True)
except BaseException:
    error=traceback.format_exc();(out/'status.json').write_text(json.dumps({'status':'failed','error':error},indent=2));print(error,flush=True);raise
