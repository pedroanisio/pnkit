from pathlib import Path
import json,shutil,xml.etree.ElementTree as ET,subprocess,sys
root=Path(__file__).resolve().parents[1];folder=root/'26-rich-2d-count'
archive=root/'work/vitrine26-r2';archive.mkdir(exist_ok=True)
for name in ['scene.xml','still.png','clip.mp4','encode.json','MOTION-SAMPLES.jpg','SHA256SUMS']:
    if not (archive/name).exists():shutil.copy2(folder/name,archive/name)
tree=ET.parse(archive/'scene.xml');scene=tree.getroot();assets=scene.find('assets');composition=scene.find('composition')
count=assets.find("text[@id='countAsset']");count.set('style','pn-heading');count.set('weight','700');count.set('size','64');count.set('text','12 PEÇAS')
for child in list(count):count.remove(child)
for i in range(8):
    value=ET.SubElement(assets,'text',dict(count.attrib));value.set('id',f'count{i}');value.set('text',str((i+1)*12)+' PEÇAS')
final=ET.SubElement(assets,'text',dict(count.attrib));final.set('id','countFinal');final.set('text','23 DE 96')
assets.append(ET.fromstring('<text id="denseLabel" text="365 PEÇAS · 14 PX" style="pn-heading" fontFile="../assets/archivo.ttf" size="48" weight="700" color="#E8BC79" width="888" height="80"/>'))
assets.find("text[@id='titleAsset']").set('text','A QUANTIDADE MUDA')
assets.find("text[@id='subAsset']").set('text','96 em ondas / 23 selecionadas / densidade 365')
composition.remove(composition.find("group[@id='board']"))
body='''<group id="counts" x="100" y="680" width="888" height="1000" effects="contactFX">

<repeat id="rows" count="8" offsetY="50" timeStep="0.2"><shape id="cell" shape="rect" width="58" height="34" radius="4" fill="#D8C496" stroke="#96825F" strokeWidth="1.5" threeD="true" zDepth="0"><shapeModifier type="repeater" copies="12" offsetX="72"/></shape></repeat>
<group id="selected" start="1.8">
<shape id="connector" shape="path" width="888" height="120" path="M 29 17 H 821 L 749 67 H 29" fill="#00000000" stroke="#77989B" strokeWidth="1.5" threeD="true" zDepth="0"/>
<shape id="highlightRowA" shape="rect" width="58" height="34" radius="4" fill="#3BBBA9" stroke="#218678" strokeWidth="1.5" threeD="true" zDepth="0"><shapeModifier type="repeater" copies="12" offsetX="72"/></shape>
<shape id="highlightRowB" shape="rect" y="50" width="58" height="34" radius="4" fill="#3BBBA9" stroke="#218678" strokeWidth="1.5" threeD="true" zDepth="0"><shapeModifier type="repeater" copies="11" offsetX="72"/></shape>
<shape id="groupOutline" shape="path" width="888" height="120" path="M -8 -8 H 858 V 42 H 786 V 92 H -8 Z" fill="#00000000" stroke="#87BAC2" strokeWidth="3" threeD="true" zDepth="0"/>
<shape id="namedPiece" shape="rect" width="58" height="34" radius="4" fill="#3BBBA9" stroke="#F5E1AA" strokeWidth="6" threeD="true" zDepth="0"/>
</group>
<layer id="densityNumber" asset="denseLabel" y="480" threeD="true" zDepth="0"/>
<repeat id="denseRows" count="14" offsetY="24" y="550"><shape id="denseCell" shape="rect" width="14" height="14" radius="2" fill="#D8C496" threeD="true" zDepth="0"><shapeModifier type="repeater" copies="25" offsetX="32"/></shape></repeat>
<shape id="denseTail" shape="rect" y="886" width="14" height="14" radius="2" fill="#D8C496" threeD="true" zDepth="0"><shapeModifier type="repeater" copies="15" offsetX="32"/></shape>
</group>'''
counts=ET.fromstring(body)
for i in range(8):
    ET.SubElement(counts,'layer',id=f'number{i}',asset=f'count{i}',y='-90',threeD='true',zDepth='0',start=str(i*.2),end=str((i+1)*.2 if i<7 else 1.8))
ET.SubElement(counts,'layer',id='numberFinal',asset='countFinal',y='-90',threeD='true',zDepth='0',start='1.8')
composition.insert(2,counts);ET.indent(tree);tree.write(folder/'scene.xml',encoding='utf-8',xml_declaration=True)
items=json.loads((root/'work/catalog.json').read_text())
for item in items:
    if item['slug']==folder.name:
        item['title']='A quantidade muda';item['still']=3
        item['notes']='96 peças chegam em oito ondas de12, e o número sobe por camadas com janelas start/end no mesmo instante. Ao final,23 peças mudam de cor. Outra grade mostra365 peças reais de14px. Sem cartão: as peças e números ocupam o campo.'
        item['params']='12×8=96; timeStep .2, contador discreto12→96;23 destacados. Densidade25×14+15=365,14px. Conector1.5, grupo3, peça6. Archivo caps700/wdth75; câmera z-1500→-1407.'
        item['limits']='Contagens de demonstração, sem dado factual. Sobreposições recolorem peças existentes. A segunda grade é intencionalmente uma textura na escala de telefone; o número e a cor carregam leitura. threeD nos shapes/layers, não apenas no grupo.'
(root/'work/catalog.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(root/'work/render_stills.py'),folder.name],stdin=subprocess.DEVNULL,check=True)
