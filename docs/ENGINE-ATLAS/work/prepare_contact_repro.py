from pathlib import Path
import xml.etree.ElementTree as ET
import shutil,json,hashlib
root=Path(__file__).resolve().parents[1]
source=Path('/home/pals/videos/shorts/s12-why-bridges-have-gaps/work/art/looktest/sig.scene.xml')
out=root/'work/contact-shadow-repro'; out.mkdir(exist_ok=True)
(out/'assets').mkdir(exist_ok=True)
tree=ET.parse(source)
paths=['src','fontFile','baseColorMap','normalMap','metallicRoughnessMap','occlusionMap','emissiveMap','displacementMap','environment','ies']
for el in tree.iter():
    for key in paths:
        if key in el.attrib:
            old=Path(el.get(key)); old=old if old.is_absolute() else source.parent/old
            old=old.resolve(); target=out/'assets'/old.name
            shutil.copy(old,target); el.set(key,'assets/'+old.name)
(out/'source-snapshot.xml').write_text(ET.tostring(tree.getroot(),encoding='unicode'))
(out/'source.json').write_text(json.dumps(dict(source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),note='Snapshot received with no explicit contactShadows. A/B variants differ only on sun.contactShadows.'),indent=2))
for state in ['on','off']:
    tree.getroot().find("lights/light[@id='sun']").set('contactShadows','true' if state=='on' else 'false')
    tree.write(out/f'full-{state}.xml',encoding='utf-8',xml_declaration=True)
minimal=ET.fromstring(ET.tostring(tree.getroot()))
comp=minimal.find('composition')
for el in list(comp):
    if el.get('id') not in ['c','road']: comp.remove(el)
minimal.remove(minimal.find('effects'))
comp.find('camera').set('depthOfField','false')
for el in minimal.find('materials'):
    if el.get('id')=='m-asph':
        el.attrib.clear(); el.attrib.update(id='m-asph',baseColor='#808080',roughness='0.88')
for state in ['on','off']:
    minimal.find("lights/light[@id='sun']").set('contactShadows','true' if state=='on' else 'false')
    ET.ElementTree(minimal).write(out/f'minimal-{state}.xml',encoding='utf-8',xml_declaration=True)
print(out)
