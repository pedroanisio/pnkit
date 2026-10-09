from pathlib import Path
import subprocess,sys,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
root=Path(__file__).resolve().parents[1];folder=root/'26-rich-2d-count'
subprocess.run([sys.executable,str(root/'work/verify_audio_count.py')],stdin=subprocess.DEVNULL,check=True)
sheet=Image.new('RGB',(870,555),'#101C2A');d=ImageDraw.Draw(sheet);font=ImageFont.truetype(str(root/'assets/archivo.ttf'),22)
bounds=[]
for i,t in enumerate([.25,1.75,3.25]):
    out=folder/'samples'/('t'+str(t)+'.png')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-ss',str(t),'-i',str(folder/'clip.mp4'),'-frames:v','1','-y',str(out)],stdin=subprocess.DEVNULL,check=True)
    im=Image.open(out).convert('RGB');a=np.array(im);m=(a[:,:,0]>150)&(a[:,:,1]>140)&(a[:,:,2]<190);m[:800]=False
    m[1600:]=False
    ys,xs=np.where(m);bounds.append(dict(time=t,first_x=int(xs.min()),last_x=int(xs.max()),width=int(xs.max()-xs.min()+1)))
    im.thumbnail((270,480));sheet.paste(im,(i*290+10,10));d.text((i*290+10,505),str(t)+' s',font=font,fill='white')
sheet.save(folder/'MOTION-SAMPLES.jpg',quality=95)
(folder/'camera-check.json').write_text(json.dumps(bounds,indent=2));print('Camera',bounds,flush=True)
hashes=[]
for name in ['scene.xml','still.png','clip.mp4','encode.json','MOTION-SAMPLES.jpg','camera-check.json']:
    p=folder/name;hashes.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name)
(folder/'SHA256SUMS').write_text('\n'.join(hashes)+'\n')
