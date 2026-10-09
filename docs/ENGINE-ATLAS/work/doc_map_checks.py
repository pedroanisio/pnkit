from pathlib import Path
import subprocess, json
from PIL import Image, ImageDraw
import numpy as np
root=Path(__file__).resolve().parents[1]
binary='/home/pals/.local/share/scene-render/bin/scene-render-premium'
out=root/'work/doc-map-checks';out.mkdir(exist_ok=True)
text='''<scene version="1.1"><project width="200" height="60" fps="10" duration="1" background="#000000"/><styles><token name="brand-red" value="#FF0000"/><textStyle id="t-base" color="var(--brand-red)"/><textStyle id="t-red" basedOn="t-base" size="44"/></styles><assets><text id="t" text="HHHH" size="44" width="200" height="60" fontFile="../../assets/atlas.ttf" style="t-red" ATTR/></assets><composition><layer id="lt" asset="t"/></composition></scene>'''
checks={}
for name,attr in [('style',''),('explicit','color="#00FF00"')]:
    p=out/(name+'.xml');p.write_text(text.replace('ATTR',attr))
    r=subprocess.run([binary,'render',str(p),'-o',str(out/(name+'.png')),'--strict','--quality','final'],stdin=subprocess.DEVNULL,capture_output=True,text=True)
    (out/(name+'.log')).write_text(r.stdout+r.stderr)
    a=np.array(Image.open(out/(name+'.png')).convert('RGB'))
    checks[name]=dict(exit=r.returncode,mean_rgb=a.mean(axis=(0,1)).tolist())
xml=(root/'23-native-map-relief/scene.xml').read_text()
sheet=Image.new('RGB',(810,510),'#101C2A'); d=ImageDraw.Draw(sheet)
for i,(name,zoom,exag,tilt) in enumerate([('map-a',11,3,-65),('map-b',12,4,-65),('map-c',11,5,-55)]):
    candidate=xml.replace('terrain="dem" exaggeration="1.2"','terrain="dem" exaggeration="'+str(exag)+'"').replace('zoom="12"','zoom="'+str(zoom)+'"').replace('rotationX="-45"','rotationX="'+str(tilt)+'"').replace('intensity="450"','intensity="130"').replace('intensity="330"','intensity="80"').replace('contactShadows="true"','contactShadows="false"').replace('../assets/','../../assets/')
    p=out/(name+'.xml');p.write_text(candidate)
    r=subprocess.run([binary,'render',str(p),'--time','1.75','-o',str(out/(name+'.png')),'--strict','--quality','final'],stdin=subprocess.DEVNULL,capture_output=True,text=True)
    (out/(name+'.log')).write_text(r.stdout+r.stderr); checks[name]=dict(exit=r.returncode,zoom=zoom,exaggeration=exag,tilt=tilt)
    im=Image.open(out/(name+'.png')).convert('RGB');im.thumbnail((270,480));sheet.paste(im,(i*270,0));d.text((i*270+8,485),name,fill='white')
sheet.save(out/'MAP-CANDIDATES.jpg',quality=95)
(out/'checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
