from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];d=root/'27-caption-source-breaks';clip=d/'clip.mp4'
p=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(clip)],stdin=subprocess.DEVNULL,capture_output=True,text=True,check=True);s=json.loads(p.stdout)['streams'][0]
assert (s['width'],s['height'],s['r_frame_rate'],int(s['nb_read_frames']))==(1080,1920,'24/1',84),s
assert abs(float(s['duration'])-3.5)<0.001,s
p=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(clip),'-f','null','-'],stdin=subprocess.DEVNULL,capture_output=True,text=True,check=True);assert not p.stderr,p.stderr
sheet=Image.new('RGB',(1080,680),'#0b1620');draw=ImageDraw.Draw(sheet)
for i,t in enumerate([0.25,1.75,3.25]):
 out=d/f'decoded-{t:.2f}.png';subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss',str(t),'-i',str(clip),'-frames:v','1',str(out)],stdin=subprocess.DEVNULL,check=True)
 im=Image.open(out).convert('RGB');im.thumbnail((360,640));sheet.paste(im,(360*i,32));draw.text((360*i+12,8),f't={t:.2f}s / frame {round(t*24)}',fill='white')
sheet.save(d/'MOTION-SAMPLES.jpg',quality=95)
proof=dict(stream=s,decode_errors=p.stderr,source='84 native cargo-test-library renderer frames, h264_nvenc via sr-gpu',sample_times=[0.25,1.75,3.25],playback='not directly watched; sampled encoded frames inspected')
(d/'clip-check.json').write_text(json.dumps(proof,indent=2));print(proof)
