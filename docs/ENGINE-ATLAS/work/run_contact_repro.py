from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
import numpy as np
root=Path(__file__).resolve().parents[1]; out=root/'work/contact-shadow-repro'
binary='/home/pals/.local/share/scene-render/bin/scene-render-premium'
metrics=[]; board=Image.new('RGB',(1080,1100),'#101C2A');draw=ImageDraw.Draw(board);font=ImageFont.truetype(str(root/'assets/atlas.ttf'),24)
for row,kind in enumerate(['full','minimal']):
    imgs={}
    for col,state in enumerate(['off','on']):
        with (out/f'{kind}-{state}.log').open('w') as log:
            subprocess.run([binary,'render',str(out/f'{kind}-{state}.xml'),'--time','0','-o',str(out/f'{kind}-{state}.png'),'--strict','--quality','final'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,check=True)
        im=Image.open(out/f'{kind}-{state}.png').convert('RGB');imgs[state]=np.asarray(im,dtype=float)
        crop=im.crop((0,500,1080,1450));crop.thumbnail((520,500));board.paste(crop,(col*540+10,row*550+45));draw.text((col*540+10,row*550+10),f'{kind} / {state}',font=font,fill='#F4EFE4')
    for name,(x0,y0,x1,y1) in {'road-mid':(220,800,850,1200),'road-near':(220,1250,850,1440),'sky-control':(200,80,850,200)}.items():
        off=imgs['off'][y0:y1,x0:x1];on=imgs['on'][y0:y1,x0:x1];weights=np.array([.2126,.7152,.0722])
        metrics.append(dict(kind=kind,region=name,box=[x0,y0,x1,y1],mean_luma_off=float((off@weights).mean()),mean_luma_on=float((on@weights).mean()),mean_abs_difference=float(np.abs(off-on).mean()),fraction_changed_over_8=float((np.abs(off-on).max(axis=2)>8).mean())))
(out/'metrics.json').write_text(json.dumps(metrics,indent=2));board.save(out/'COMPARISON.jpg',quality=95)
print(json.dumps(metrics,indent=2))
