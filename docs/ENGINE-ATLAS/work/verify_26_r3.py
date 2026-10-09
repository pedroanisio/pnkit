from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
root=Path(__file__).resolve().parents[1];folder=root/'26-rich-2d-count';samples=folder/'samples';samples.mkdir(exist_ok=True)
def components(mask,threshold):
    visited=np.zeros(mask.shape,bool);areas=[]
    for y,x in zip(*np.where(mask)):
        if visited[y,x]:continue
        stack=[(y,x)];visited[y,x]=True;area=0
        while stack:
            yy,xx=stack.pop();area+=1
            for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
                ny,nx=yy+dy,xx+dx
                if 0<=ny<mask.shape[0] and 0<=nx<mask.shape[1] and mask[ny,nx] and not visited[ny,nx]:visited[ny,nx]=True;stack.append((ny,nx))
        if area>threshold:areas.append(area)
    return len(areas)
checks=[];sheet=Image.new('RGB',(870,555),'#101C2A');d=ImageDraw.Draw(sheet);font=ImageFont.truetype(str(root/'assets/archivo.ttf'),22)
for t in [.083333,.291667,.5,.708333,.916667,1.125,1.333333,1.541667,3.25]:
    dest=samples/f'count-{t:.6f}.png';subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-y','-ss',str(t),'-i',str(folder/'clip.mp4'),'-frames:v','1',str(dest)],stdin=subprocess.DEVNULL,check=True)
    im=Image.open(dest).convert('RGB');a=np.asarray(im);gold=(a[:,:,0]>145)&(a[:,:,1]>125)&(a[:,:,2]<190)&(a[:,:,0]>a[:,:,2]+25);cyan=(a[:,:,1]>120)&(a[:,:,2]>90)&(a[:,:,1]>a[:,:,0]*1.4)
    upper=(gold|cyan)[660:1110,90:985];low=gold[1210:1620,90:985]
    actual=components(upper,400);selected=components(cyan[660:1110,90:985],400);dense=components(low,45)
    expected=min(96,(int(t/.2)+1)*12)
    checks.append(dict(time=t,pieces=actual,expected=expected,selected=selected,density=dense,pass_check=actual==expected and dense==365 and selected==(23 if t>=1.8 else 0)))
for j,t in enumerate([.25,1.75,3.25]):
    dest=samples/f't{t:.2f}.png';subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-y','-ss',str(t),'-i',str(folder/'clip.mp4'),'-frames:v','1',str(dest)],stdin=subprocess.DEVNULL,check=True)
    im=Image.open(dest).convert('RGB');im.thumbnail((270,480));sheet.paste(im,(j*290+10,10));d.text((j*290+10,505),f'{t:.2f} s',font=font,fill='white')
sheet.save(folder/'MOTION-SAMPLES.jpg',quality=95);(folder/'count-check.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks),flush=True)
(folder/'SHA256SUMS').write_text(''.join(hashlib.sha256((folder/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in ['scene.xml','still.png','clip.mp4','encode.json','MOTION-SAMPLES.jpg','count-check.json']))
if not all(x['pass_check'] for x in checks):raise SystemExit(1)
