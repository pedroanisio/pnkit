from build_showcase import *
from PIL import Image,ImageDraw
# Rectangular studio windows in original, linear RGBE environment.
w,h=256,128
with (assets/'window-studio.hdr').open('wb') as stream:
    stream.write(f'#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y {h} +X {w}\n'.encode())
    for yy in range(h):
        for xx in range(w):
            on=(35<xx<85 and 28<yy<65 and not 58<xx<62 and not 45<yy<49) or (175<xx<200 and 23<yy<90)
            rgb=[8,7.4,6.1] if on else [.07,.10,.16];m=max(rgb);mant,e=math.frexp(m);scale=mant*256/m
            stream.write(bytes([min(255,int(v*scale)) for v in rgb]+[e+128]))
body=FLOOR+'<object3D id="kettle" primitive="mesh" mesh="kettleAsset" x="500" y="1424" z="0" material="steel">'+anim('rotationY',-15,20)+'</object3D><object3D id="handle" primitive="torus" radius="110" height="22" segments="96" x="735" y="1210" z="40" rotationX="90" material="steel"/><object3D id="lid" primitive="sphere" radius="34" segments="64" x="500" y="1035" z="0" material="black"/>'
write('02-hdri-ao-ssr','O laboratório se reflete','Janelas no HDRI / contato AO / piso SSR',body,camera=CAM.replace('aoRadius="35"','aoRadius="65"').replace('/>',' screenSpaceReflections="true"/>'),lights=LIGHTS.replace('../assets/studio.hdr','../assets/window-studio.hdr').replace('intensity="0.32"','intensity="0.7"'),mats=MATS.replace('roughness="0.24"','roughness="0.06"').replace('baseColor="#141C20" roughness="0.55"','baseColor="#141C20" roughness="0.08" metallic="0.5"'),extra_assets='<mesh id="kettleAsset" src="../assets/kettle.obj" format="obj"/>')
# Textured paper cutouts preserve the original alpha and mountain silhouette.
rng=np.random.default_rng(104)
for i in range(3):
    im=Image.open(assets/f'plate{i}.png').convert('RGBA');a=np.array(im);noise=rng.normal(0,6,a.shape[:2])+3*np.sin(np.indices(a.shape[:2])[0]*2.4)
    a[:,:,:3]=np.clip(a[:,:,:3].astype(float)+noise[:,:,None],0,255);Image.fromarray(a).save(assets/f'paper-mountain{i}.png')
im=Image.new('RGBA',(1040,300));a=np.array(im);yy=np.arange(300);alpha=(np.exp(-((yy-150)/90)**2)*55).astype('uint8');a[:,:,:3]=[184,207,209];a[:,:,3]=alpha[:,None];Image.fromarray(a).save(assets/'mist.png')
plateassets=''.join(f'<image id="plateAsset{i}" src="../assets/paper-mountain{i}.png" width="{r*2}" height="{r*2}"/>' for i,r in [(0,520),(1,370),(2,220)])+'<image id="mistAsset" src="../assets/mist.png" width="1040" height="300"/>'
plates='<shape id="moon" shape="ellipse" width="160" height="160" x="740" y="700" fill="#F3DCAD" threeD="true" zDepth="800"/>'
for i,(z,r,x,y) in enumerate([(700,520,600,1060),(0,370,550,1160),(-450,220,360,1270)]):
    plates+=f'<layer id="plate{i}" asset="plateAsset{i}" threeD="true" zDepth="{z}" x="{x}" y="{y}" anchorX="{r}" anchorY="{r}"/>'
    if i<2:plates+=f'<layer id="fog{i}" asset="mistAsset" x="20" y="1200" threeD="true" zDepth="{z-100}"/>'
write('04-25d-parallax','A paisagem tem profundidade','Papel em três planos / neblina / paralaxe',plates,camera='<camera id="cam" fov="42" x="540" y="750" z="-1400" pitch="-7">'+anim('x',450,630)+'</camera>',lights='',mats='',extra_assets=plateassets)
# Hourglass silhouette traced as a genuine closed mesh; sand is an illustrative solid.
lathe('hourglass',[(0,0),(115,0),(120,-25),(108,-85),(60,-165),(16,-205),(16,-230),(60,-270),(108,-350),(120,-405),(115,-430),(0,-430)])
body=FLOOR+'<object3D id="glassBody" primitive="mesh" mesh="hourglassAsset" x="540" y="1395" z="0" material="glass"/><object3D id="bottom" primitive="cylinder" radius="145" height="30" segments="96" x="540" y="1410" z="0" material="brass"/><object3D id="top" primitive="cylinder" radius="145" height="30" segments="96" x="540" y="950" z="0" material="brass"/><object3D id="sand" primitive="cone" radius="86" height="130" segments="64" x="540" y="1330" z="0" material="paper"/>'
for x in [400,680]:body+=f'<object3D id="pillar{x}" primitive="cylinder" radius="10" height="430" segments="32" x="{x}" y="1180" z="25" material="brass"/>'
write('05-pathtrace-hero','O tempo atravessa o vidro','Ampulheta / path tracer / 128 amostras',body,camera=CAM.replace('/>',' renderer="pathtrace" pathSamples="128" maxBounces="6" denoise="true"/>'),lights=LIGHTS.replace('intensity="0.32"','intensity="0.7"'),extra_assets='<mesh id="hourglassAsset" src="../assets/hourglass.obj" format="obj"/>')
# Original optical sprite: soft cream disk with brighter rim and partial alpha.
y,x=np.mgrid[:128,:128];r=np.sqrt(((x-63.5)/63.5)**2+((y-63.5)/63.5)**2);rgba=np.zeros((128,128,4),dtype=np.uint8);rgba[:,:,:3]=[255,234,199];rgba[:,:,3]=(np.clip(.28+.12*np.exp(-((r-.8)/.1)**2),0,1)*np.clip((1-r)*10,0,1)*255).astype('uint8');Image.fromarray(rgba).save(assets/'bokeh-disk.png')
# Clearer native discs with soft additive glow, emitted along a path and asset alpha.
body='''<shape id="beam" shape="path" path="M 940 680 L 300 1510 L 760 1540 Z" width="1080" height="1600" fill="#E7CB8C" opacity="0.055"/>
<particleEmitter id="dust" preset="dust" x="0" y="0" emitterShape="path" emitterPath="M 390 1460 C 460 1120 780 880 920 720" rate="140" lifetime="6" speed="12" size="3" color="#FFEFD0" opacity="0.45" blend="add" preroll="3" seed="11"/>
<particleEmitter id="bokeh" preset="bokeh" shape="sprite" sprite="bokehSprite" x="240" y="850" emitterShape="asset-alpha" emitterAsset="ringAlpha" rate="9" lifetime="6" speed="30" spread="360" size="38" sizeEnd="45" sizeVariance="14" color="#FFE6B7" opacity="1" opacityEnd="0.2" blend="add" preroll="4" seed="12"/>'''
write('07-particles-path-alpha','A luz encontra a poeira','Feixe / poeira no caminho / bokeh no alpha',body,camera='',lights='',mats='',extra_assets='<image id="ringAlpha" src="../assets/ring-alpha.png" width="320" height="320"/><image id="bokehSprite" src="../assets/bokeh-disk.png" width="128" height="128"/>')
for item in catalog:
    item['notes']=item['notes'].replace(' Vitrine revisada: Archivo, subtítulo36, assunto próprio e piso sem borda no enquadramento.','')+' Vitrine revisada: Archivo, subtítulo36 e assunto próprio.'
    if item['slug']=='02-hdri-ao-ssr':item['params']='Bule OBJ cromado, roughness .06; HDRI original de janelas RGBE dome.7; AO radius65/intensity1.25; SSR piso roughness.08. A/B desliga AO/SSR com mesmas luzes.'
    if item['slug']=='04-25d-parallax':item['params']='Montanhas de papel texturizado, moon z800, mist entre planos; z700/0/-450; câmera x450→630.'
    if item['slug']=='05-pathtrace-hero':item['params']='Ampulheta OBJ original, vidro e latão; pathSamples128,maxBounces6,denoise; still apenas.';item['limits']='Areia é sólido ilustrativo, não simulação granular. Vidro não gera cáusticas; 128 amostras ainda exigem medir ruído e custo.'
    if item['slug']=='07-particles-path-alpha':item['params']='Poeira140/s no caminho, size3; bokeh9/s em alpha, size38→45,var14, opacity.3, add; seed11/12,preroll3/4.'
(root/'work/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
