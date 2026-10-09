from pathlib import Path
import xml.etree.ElementTree as ET,shutil,json,sys,subprocess
root=Path(__file__).resolve().parents[1]
shutil.copy('/home/pals/videos/lib/docs/fonts/Archivo-wdth-wght.ttf',root/'assets/archivo.ttf')
shutil.copy('/home/pals/videos/lib/docs/fonts/OFL-archivo.txt',root/'assets/OFL-archivo.txt')
archive=root/'work/technical-v1';archive.mkdir(exist_ok=True)
items=json.loads((root/'work/catalog.json').read_text())
styles_xml='''<styles><textStyle id="pn-heading" fontAsset="pn-archivo" size="64" weight="700" variation="wght 700, wdth 75"/><textStyle id="pn-subtitle" fontAsset="pn-archivo" size="36" weight="400" variation="wght 400, wdth 90"/></styles>'''
for item in items:
    folder=root/item['slug'];old=archive/item['slug'];old.mkdir(exist_ok=True)
    for name in ['scene.xml','still.png','clip.mp4','README.md','encode.json','render.log','encode.log']:
        if (folder/name).exists() and not (old/name).exists(): shutil.copy2(folder/name,old/name)
    p=folder/'scene.xml';tree=ET.parse(p);scene=tree.getroot();assets=scene.find('assets')
    if not assets.find("font[@id='pn-archivo']") is not None:
        assets.insert(0,ET.fromstring('<font id="pn-archivo" src="../assets/archivo.ttf" family="Archivo" weight="400" license="OFL-1.1"/>'))
    styles=scene.find('styles')
    if styles is None:
        styles=ET.fromstring(styles_xml);scene.insert(1,styles)
    elif styles.find("textStyle[@id='pn-heading']") is None:
        for node in ET.fromstring(styles_xml): styles.append(node)
    for node in assets.findall('text'):
        node.set('fontFile','../assets/archivo.ttf')
        if node.get('id')=='titleAsset':
            node.set('text',node.get('text').upper());node.set('style','pn-heading');node.set('weight','700')
        elif node.get('id')=='subAsset': node.set('size','36');node.set('style','pn-subtitle');node.set('height','130')
    ET.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)
print('Archivo aplicado; versão técnica preservada em work/technical-v1',flush=True)
if sys.argv[1:]: subprocess.run([sys.executable,str(root/'work/render_stills.py'),*sys.argv[1:]],stdin=subprocess.DEVNULL,check=True)
