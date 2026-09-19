from pathlib import Path
import sys,subprocess
R=Path(__file__).parent;sys.path.insert(0,str(R.parent/'projection_enclosed_v05/tool_packages'))
import imageio_ffmpeg
ff=imageio_ffmpeg.get_ffmpeg_exe()
for f in (R/'projection/examples').glob('*_RGB.mp4'):
 out=f.with_name(f.name.replace('_1024x786_RGB','_Browser'))
 subprocess.run([ff,'-v','error','-y','-i',str(f),'-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-crf','16','-preset','fast','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-color_range','tv','-movflags','+faststart',str(out)],check=True)
 print('BROWSER_COPY',out.name,flush=True)
