from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
import numpy as np
root=Path(__file__).resolve().parents[1]
font=ImageFont.truetype(str(root/'assets/atlas.ttf'),18)
results=[]
for item in json.loads((root/'work/catalog.json').read_text()):
    folder=root/item['slug']; clip=folder/'clip.mp4'
    if not clip.exists():continue
    frames=[]; contact=Image.new('RGB',(3*290,555),'#101C2A'); draw=ImageDraw.Draw(contact)
    samples=folder/'samples'; samples.mkdir(exist_ok=True)
    for j,t in enumerate([.25,1.75,3.25]):
        dest=samples/f't{t:.2f}.png'
        subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-y','-ss',str(t),'-i',str(clip),'-frames:v','1',str(dest)],stdin=subprocess.DEVNULL,check=True)
        im=Image.open(dest).convert('RGB'); frames.append(np.asarray(im,dtype=np.float32)); im.thumbnail((270,480)); contact.paste(im,(j*290+10,10));draw.text((j*290+10,505),f'{t:.2f} s',font=font,fill='#F4EFE4')
    contact.save(folder/'MOTION-SAMPLES.jpg',quality=94)
    delta=float(np.abs(frames[0][600:1600]-frames[2][600:1600]).mean())
    results.append(dict(slug=item['slug'],samples=[.25,1.75,3.25],subject_region_mean_absolute_difference=delta,limitation='Frame difference confirms change, not perceptual motion quality.'))
(root/'work/sampling.json').write_text(json.dumps(results,indent=2))
print('Amostrados',len(results),'clipes')
