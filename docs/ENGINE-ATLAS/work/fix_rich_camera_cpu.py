from pathlib import Path
import subprocess,sys,json
root=Path(__file__).resolve().parents[1];p=root/'26-rich-2d-count/scene.xml'
xml=p.read_text().replace('threeD="true" zDepth="0" effects="contactFX"','effects="contactFX"')
for before in ['strokeWidth="3"/>','x="40" y="48"/>','strokeWidth="1.5"><shapeModifier','strokeWidth="6"/>']:
    after=before.replace('/>',' threeD="true" zDepth="0"/>').replace('><shapeModifier',' threeD="true" zDepth="0"><shapeModifier')
    xml=xml.replace(before,after)
p.write_text(xml)
catalog=json.loads((root/'work/catalog.json').read_text())
for item in catalog:
    if item['slug']=='26-rich-2d-count': item['limits']+=' Aplique threeD aos shapes/layers, não só ao grupo transparente que os contém.'
(root/'work/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(root/'work/render_stills.py'),'26-rich-2d-count'],stdin=subprocess.DEVNULL,check=True)
