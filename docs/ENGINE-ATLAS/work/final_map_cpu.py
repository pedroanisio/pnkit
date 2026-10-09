from pathlib import Path
import subprocess,sys,json
root=Path(__file__).resolve().parents[1]
p=root/'23-native-map-relief/scene.xml'
candidate=(root/'work/doc-map-checks/map-b.xml').read_text().replace('../../assets/','../assets/').replace('z="-1400"','z="-1100"')
p.write_text(candidate)
catalog=json.loads((root/'work/catalog.json').read_text())
for item in catalog:
    if item['slug']=='23-native-map-relief':
        item['notes']='Um map asset é drapeado num mesh, elevado por tiles Terrarium e iluminado no renderer 3D. O exagero vertical de 4× torna a encosta legível nesta demonstração.'
        item['params']='Web Mercator zoom12, terrain DEM, resolution96, texture768, exaggeration4; tilt -65°; câmera z -1100.'
        item['limits']+=' Contact shadows desligadas no plano; shadow maps preservados.'
(root/'work/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(root/'work/render_stills.py'),'23-native-map-relief'],stdin=subprocess.DEVNULL,check=True)
