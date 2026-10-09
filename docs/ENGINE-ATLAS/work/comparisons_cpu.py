from pathlib import Path
import subprocess,xml.etree.ElementTree as ET,json,hashlib
from PIL import Image,ImageDraw,ImageFont
import numpy as np
root=Path(__file__).resolve().parents[1];binary='/home/pals/.local/share/scene-render/bin/scene-render-premium';records=[]
for slug,kind,labels in [('01-pbr-key-rim','rim',['KEY','KEY + RIM']),('02-hdri-ao-ssr','ambient',['SEM AO / SSR','COM AO / SSR']),('08-grade-lut-look','lut',['SEM LUT','COM LUT'])]:
    folder=root/slug;tree=ET.parse(folder/'scene.xml');scene=tree.getroot()
    if kind=='rim':scene.find('lights').remove(scene.find("lights/light[@id='rim']"))
    elif kind=='ambient':
        cam=scene.find('composition/camera');cam.set('ambientOcclusion','false');cam.set('screenSpaceReflections','false')
    else:
        cm=scene.find('colorManagement');cm.attrib.pop('looks',None)
        for look in list(cm):cm.remove(look)
    ET.indent(tree);tree.write(folder/'before.scene.xml',encoding='utf-8',xml_declaration=True)
    p=subprocess.run([binary,'render',str(folder/'before.scene.xml'),'--time','1.75','-o',str(folder/'before.png'),'--strict','--quality','final'],stdin=subprocess.DEVNULL,capture_output=True,text=True)
    (folder/'comparison-render.log').write_text(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    # Native render comparison presented in a contact sheet; crop only, no colour edits.
    a=Image.open(folder/'before.png').convert('RGB');b=Image.open(folder/'still.png').convert('RGB')
    sheet=Image.new('RGB',(1080,1320),'#10191E');d=ImageDraw.Draw(sheet);font=ImageFont.truetype(str(root/'assets/archivo.ttf'),36)
    for j,im in enumerate([a,b]):
        crop=im.crop((0,550,1080,1600));crop.thumbnail((504,490));sheet.paste(crop,(28+j*520,140));d.text((32+j*520,74),labels[j],font=font,fill='#F4EFE4')
    d.text((32,690),'MESMA CÂMERA / MESMO INSTANTE',font=font,fill='#A8BCCB');d.text((32,780),slug,font=font,fill='#E8BC79');sheet.save(folder/'COMPARISON.jpg',quality=95)
    delta=float(np.abs(np.asarray(a,dtype=float)[550:1600]-np.asarray(b,dtype=float)[550:1600]).mean());records.append(dict(slug=slug,subject_mean_absolute_difference=delta,changes=labels,limitations='Cropped native renders; mean pixel change is not an aesthetic score.'))
# Rectangle controlled repro: remove only authored behindGlass, retain all other source settings.
folder=root/'work/glass-rectangle-repro';folder.mkdir(exist_ok=True);src=root/'work/technical-v1/06-materials/scene.xml';tree=ET.parse(src);scene=tree.getroot()
for el in scene.iter():
    for k,v in list(el.attrib.items()):
        if v.startswith('../assets/'):el.set(k,'../../assets/'+v.split('/')[-1])
comp=scene.find('composition');box=comp.find("object3D[@id='behindGlass']");assert box is not None;comp.remove(box);ET.indent(tree);tree.write(folder/'without-box.xml',encoding='utf-8',xml_declaration=True)
p=subprocess.run([binary,'render',str(folder/'without-box.xml'),'--time','1.75','-o',str(folder/'without-box.png'),'--strict','--quality','final'],stdin=subprocess.DEVNULL,capture_output=True,text=True);(folder/'render.log').write_text(p.stdout+p.stderr)
if p.returncode:raise RuntimeError(p.stdout+p.stderr)
before=Image.open(src.parent/'still.png').convert('RGB');after=Image.open(folder/'without-box.png').convert('RGB');sheet=Image.new('RGB',(1080,1100),'#10191E');d=ImageDraw.Draw(sheet);f=ImageFont.truetype(str(root/'assets/archivo.ttf'),32)
for j,im in enumerate([before,after]):
    crop=im.crop((480,550,1080,1200));crop.thumbnail((500,800));sheet.paste(crop,(20+j*535,110));d.text((20+j*535,30),['COM BOX AUTORAL','SEM BOX AUTORAL'][j],font=f,fill='white')
sheet.save(folder/'COMPARISON.jpg',quality=95)
(folder/'source.json').write_text(json.dumps(dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),removed_node=ET.tostring(box,encoding='unicode'),finding='The rectangle is an authored behindGlass box, not evidence of an engine artifact.'),indent=2))
(root/'work/comparisons.json').write_text(json.dumps(records,indent=2));print(records,flush=True)
