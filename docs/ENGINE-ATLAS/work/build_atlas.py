from pathlib import Path
import math, json, shutil
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
shutil.copy('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', ASSETS/'atlas.ttf')
rng = np.random.default_rng(20261002)
paper = np.clip(224 + rng.normal(0, 3, (512,512,1)), 0,255)
Image.fromarray(np.repeat(paper,3,axis=2).astype('uint8')).save(ASSETS/'paper.png')
y,x = np.mgrid[:512,:512]
weave = np.clip(150 + 18*np.sin(x*math.pi/3)*np.sin(y*math.pi/3) + rng.normal(0,2,(512,512)),0,255)
Image.fromarray(np.stack([weave*.6,weave*.9,weave],axis=2).astype('uint8')).save(ASSETS/'weave.png')
im=Image.new('RGBA',(320,320)); d=ImageDraw.Draw(im); d.ellipse((30,30,290,290),fill='#FFE4AF'); d.ellipse((85,85,235,235),fill=(0,0,0,0)); im.save(ASSETS/'ring-alpha.png')
# Original procedural HDR studio: genuine linear-light RGBE data, not a fetched photograph.
w,h=256,128
with (ASSETS/'studio.hdr').open('wb') as f:
    f.write(f'#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y {h} +X {w}\n'.encode())
    for yy in range(h):
        row=[]
        for xx in range(w):
            a=xx/w; b=yy/h
            key=7*math.exp(-((a-.23)/.06)**2-((b-.32)/.15)**2)
            rim=4*math.exp(-((a-.72)/.04)**2-((b-.42)/.23)**2)
            c=[.08+key+rim*.35,.10+key*.82+rim*.75,.15+key*.60+rim]
            m=max(c); mant,e=math.frexp(m); s=mant*256/m
            row.append(bytes([min(255,int(v*s)) for v in c]+[e+128]))
        # raw scanline; decoder accepts old-style RGBE scanlines.
        f.write(b''.join(row))
with (ASSETS/'amber-teal.cube').open('w') as f:
    f.write('TITLE "Atlas subtle amber teal"\nLUT_3D_SIZE 17\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
    for b in np.linspace(0,1,17):
        for g in np.linspace(0,1,17):
            for r in np.linspace(0,1,17):
                lum=(r+g+b)/3; shadow=(1-lum)*.025
                f.write(f'{min(1,r*1.02):.6f} {min(1,g*.98+shadow):.6f} {min(1,b*.94+shadow*1.8):.6f}\n')

def anim(prop,a,b,begin=0,end=3.5):
    return f'<animate property="{prop}"><key time="{begin}" value="{a}" interpolation="sine-in-out"/><key time="{end}" value="{b}"/></animate>'

MATS='''<material id="ceramic" baseColor="#26B8AC" roughness="0.3" clearcoat="0.35"/>
<material id="gold" baseColor="#E8BC79" metallic="1" roughness="0.22"/>
<material id="floorMat" baseColor="#26394B" roughness="0.45"/>
<material id="glassMat" baseColor="#D8F5FF" transmission="1" roughness="0.025" ior="1.48" thickness="65" attenuationColor="#67CBD5" attenuationDistance="350"/>
<material id="paperMat" baseColor="#E5D9BA" baseColorMap="../assets/paper.png" roughness="0.94"/>
<material id="clothMat" baseColor="#73B7C1" baseColorMap="../assets/weave.png" roughness="0.82" sheenColor="#BBF5FF" sheenRoughness="0.55"/>'''
LIGHTS='''<light id="ambient" type="ambient" intensity="0.11" color="#AACBDD"/>
<light id="key" type="point" x="-250" y="200" z="-650" intensity="450" colorTemperature="4400" castShadow="true" shadowMapSize="1024" shadowSoftness="1.5" contactShadows="true" contactShadowLength="50"/>
<light id="rim" type="point" x="1100" y="650" z="350" intensity="330" colorTemperature="9000"/>
<light id="front" type="point" x="640" y="600" z="-900" intensity="65"/>'''
CAM='<camera id="cam" fov="42" x="540" y="750" z="-1400" pitch="-7" {attrs}>{keys}</camera>'
FLOOR='<object3D id="floor" primitive="box" width="2400" height="30" depth="2200" x="540" y="1330" z="360" material="floorMat"/>'
HERO='''<object3D id="hero" primitive="torus" radius="220" height="125" segments="64" x="460" y="1075" z="100" rotationX="65" rotationY="-15" material="ceramic">{keys}</object3D>
<object3D id="accent" primitive="sphere" radius="115" segments="48" x="770" y="1195" z="140" material="gold"/>'''

catalog=[]
def scene(slug,title,subtitle,body,*,camera='',lights='',assets='',effects='',mats=MATS,grade='',styles='',paints='',physics='',audio='',motion=True,still=1.75,notes='',params='',limits='',ideas=''):
    folder=ROOT/slug; folder.mkdir(exist_ok=True)
    xml=f'''<?xml version="1.0" encoding="UTF-8"?>
<scene version="1.2">
<project width="1080" height="1920" fps="24" duration="3.5" background="#0B1520" motionBlur="false" seed="20261002"/>
{styles}{grade}<assets><text id="titleAsset" text="{escape(title)}" fontFile="../assets/atlas.ttf" size="64" color="#F4EFE4" width="888" height="180"/>
<text id="subAsset" text="{escape(subtitle)}" fontFile="../assets/atlas.ttf" size="28" color="#A8BCCB" width="888" height="100"/>
<text id="footAsset" text="PALS / ENGINE ATLAS" fontFile="../assets/atlas.ttf" size="23" color="#A8BCCB" width="888" height="50"/>{assets}</assets>
{paints}{('<materials>'+mats+'</materials>') if mats else ''}
<composition>{camera}{body}
<layer id="title" asset="titleAsset" x="96" y="205"/>
<shape id="accentRule" shape="rect" x="96" y="400" width="94" height="5" fill="#E8BC79"/>
<layer id="sub" asset="subAsset" x="96" y="440"/>
<layer id="footer" asset="footAsset" x="96" y="1720"/>
</composition>{'<lights>'+lights+'</lights>' if lights else ''}
{('<effects>'+effects+'</effects>') if effects else ''}{physics}{audio}
</scene>'''
    (folder/'scene.xml').write_text(xml)
    entry=dict(slug=slug,title=title,motion=motion,still=still,notes=notes,params=params,limits=limits,ideas=ideas)
    catalog.append(entry)

scene('01-pbr-key-rim','Luz que desenha','PBR / key quente / recorte frio',FLOOR+HERO.format(keys=anim('rotationY',-25,15)),camera=CAM.format(attrs='',keys=''),lights=LIGHTS,
notes='Key lateral cria volume, rim frio separa o contorno; o apoio recebe sombra real.',params='Key 450 cd a ~10 m; rim 330 cd; ambient 0.11; roughness 0.30; shadowMapSize 1024.',limits='Luzes usam metros (100 unidades = 1 m). Área usa aproximação de ponto representativo. Não elevar ambient até apagar o volume.',ideas='Revelar um sensor antes de explicar sua função; distinguir duas peças por luz; mostrar o contato que causa uma força.')
scene('02-hdri-ao-ssr','O ambiente aparece','HDRI original / AO / reflexos em tela',FLOOR+HERO.format(keys=anim('rotationY',-25,15)),camera=CAM.format(attrs='ambientOcclusion="true" aoRadius="90" aoIntensity="1.2" screenSpaceReflections="true"',keys=''),lights=LIGHTS.replace('intensity="0.11"','intensity="0.04"')+'<light id="dome" type="dome" environment="../assets/studio.hdr" intensity="0.75"/>',
notes='HDRI RGBE procedural com dois softboxes. AO fecha contatos; SSR acrescenta reflexos dos objetos visíveis.',params='Dome 0.75, AO radius 90 / intensity 1.2; floor roughness 0.18 para um reflexo mais limpo.',limits='SSR perde informação fora da tela e atrás da câmera. Dome não substitui sombra de luz. O HDRI é sintético, não fotografia.',ideas='Uma peça cromada refletindo o laboratório; objeto sobre chão úmido; dar unidade a modelos de fornecedores diferentes.')
scene('03-dof-focus-pull','Olhe aqui. Agora ali.','DOF / foco do primeiro plano ao fundo',FLOOR+'''<object3D id="near" primitive="sphere" radius="105" segments="64" x="405" y="900" z="-150" material="gold"/>
<object3D id="far" primitive="torus" radius="165" height="95" segments="64" x="680" y="940" z="650" rotationX="75" material="ceramic"/>''',camera=CAM.format(attrs='depthOfField="true" focalLength="85" fStop="0.7" focusDistance="1250" apertureBlades="7"',keys=anim('focusDistance',1250,2050,.5,3)),lights=LIGHTS,
notes='A mudança de foco transfere a atenção entre objetos em profundidades diferentes.',params='85 mm, f/0.7 exagerado para tornar o efeito didático; foco 1250 → 2050 unidades entre 0.5 e 3 s; sete lâminas. Para uso natural, comece em f/1.4–2.',limits='DOF afeta object3D; placas 2.5D e texto continuam nítidos. FocalLength substitui o FOV. Checar a legibilidade depois do foco.',ideas='Do componente à máquina; do sintoma à causa no fundo; revelar qual amostra foi selecionada.')
plates=''
for i,(z,col,rad,px,py) in enumerate([(700,'#234B5B',520,600,1060),(0,'#D8BC81',370,550,1160),(-450,'#37AAA3',220,360,1270)]):
    plate=Image.new('RGBA',(rad*2,rad*2)); draw=ImageDraw.Draw(plate)
    draw.polygon([(0,rad*2),(0,rad*1.3),(rad*.45,rad*.85),(rad*.8,rad*1.1),(rad*1.3,rad*.35),(rad*1.7,rad*.95),(rad*2,rad*.7),(rad*2,rad*2)],fill=col)
    draw.line([(rad*.8,rad*1.1),(rad*1.3,rad*.35),(rad*1.7,rad*.95)],fill='#C8D8CB',width=3)
    plate.save(ASSETS/f'plate{i}.png')
    plates+=f'<layer id="plate{i}" asset="plateAsset{i}" threeD="true" zDepth="{z}" x="{px}" y="{py}" anchorX="{rad}" anchorY="{rad}"/>'
plate_assets=''.join(f'<image id="plateAsset{i}" src="../assets/plate{i}.png" width="{r*2}" height="{r*2}"/>' for i,r in [(0,520),(1,370),(2,220)])
scene('04-25d-parallax','Uma câmera. Três planos.','2.5D / zDepth / paralaxe coerente',plates,camera=CAM.format(attrs='',keys=anim('x',450,630)),assets=plate_assets,lights='',notes='Três recortes de montanha separados em z respondem a um único deslocamento de câmera.',params='zDepth 700 / 0 / -450; câmera x 450 → 630; FOV 42; âncoras no centro.',limits='Ordenação só entre irmãos threeD consecutivos. Placas não recebem DOF. Use imagem com alpha para recortes orgânicos.',ideas='Arquivo histórico em três recortes; camadas de um relevo; aproximação através de um instrumento.')
scene('05-pathtrace-hero','Luz que retorna','Path tracer / metal / vidro / sombra',FLOOR+HERO.format(keys='')+'<object3D id="glass" primitive="sphere" radius="100" segments="48" x="310" y="1220" z="-120" material="glassMat"/>',camera=CAM.format(attrs='renderer="pathtrace" pathSamples="64" maxBounces="5" denoise="true"',keys=''),lights=LIGHTS,motion=False,notes='Quadro de capa com reflexões e iluminação indireta determinísticas.',params='64 amostras, 5 bounces e denoise para ensaio; 128–256 amostras para capa, medir antes.',limits='Vidro é opaco aos raios de sombra: sem cáusticas. Denoiser pode suavizar detalhe. Custo multiplicado por amostras/pixels; reserve para hero still.',ideas='Capa de uma peça ou material; comparação de acabamento; revelar uma amostra como objeto de museu.')
materials_body=FLOOR
materials_body+='<object3D id="behindGlass" primitive="box" width="250" height="240" depth="20" x="760" y="890" z="350" material="paperMat"/>'
for i,(mat,xx,yy,zz) in enumerate([('gold',310,890,100),('glassMat',760,890,100),('paperMat',310,1250,100),('clothMat',760,1250,100)]):
    materials_body+=f'<object3D id="sample{i}" primitive="sphere" radius="160" segments="64" x="{xx}" y="{yy}" z="{zz}" material="{mat}">{anim("rotationY",0,35)}</object3D>'
scene('06-materials','A superfície explica','Metal / vidro / papel / tecido',materials_body,camera=CAM.format(attrs='',keys=''),lights=LIGHTS+'<light id="dome" type="dome" environment="../assets/studio.hdr" intensity="0.5"/>',notes='Quatro respostas à mesma luz: ouro, transmissão, papel rugoso e sheen têxtil. Texturas originais procedurais.',params='Metallic 1 / roughness .22; vidro transmission 1 / roughness .025 / ior 1.48; papel .94; tecido sheenRoughness .55.',limits='Papel e tecido são aproximações de superfície; a esfera não demonstra fibras, espessura ou dobra de tecido. Vidro requer algo visível atrás.',ideas='Comparar isolamento e reflexão; escolher material de uma cápsula; apresentar amostras antes de uma experiência.')
scene('07-particles-path-alpha','A atmosfera tem origem','Poeira no caminho / bokeh no alpha','''<shape id="orbit" shape="path" path="M 160 1180 C 160 750 910 750 910 1180 C 910 1500 160 1500 160 1180 Z" width="1080" height="1600" fill="#00000000" stroke="#436779" strokeWidth="3"/>
<layer id="ring" asset="ringAlpha" x="380" y="920" opacity="0.3"/>
<particleEmitter id="dust" preset="dust" x="0" y="0" emitterShape="path" emitterPath="M 160 1180 C 160 750 910 750 910 1180 C 910 1500 160 1500 160 1180 Z" rate="110" lifetime="6" speed="22" size="4" color="#D1E7EA" opacity="0.55" preroll="3" seed="11"/>
<particleEmitter id="bokeh" preset="bokeh" x="380" y="920" emitterShape="asset-alpha" emitterAsset="ringAlpha" rate="12" lifetime="4" speed="45" spread="360" size="14" sizeEnd="12" sizeVariance="5" color="#EDC68E" opacity="0.25" opacityEnd="0" preroll="2" seed="12"/>''',assets='<image id="ringAlpha" src="../assets/ring-alpha.png" width="320" height="320"/>',mats='',notes='Um caminho emite poeira; a silhueta opaca de um asset emite bokeh. Ambos usam seeds fixos.',params='Poeira 110/s, size 4, opacity .55; bokeh 12/s, size 14 → 12 ±5, opacity .25; preroll 2–3 s.',limits='Partículas são 2D e não recebem DOF físico. Os presets substituem atributos que ficam no default do schema: declare sizeEnd explicitamente para evitar discos gigantes. Alpha do asset define nascimentos; sprite preserva cor própria.',ideas='Resíduos saindo de uma peça; poeira de uma ruína recortada; mostrar trajetória por material suspenso.')
scene('08-grade-lut-look','Uma paleta, vários materiais','LUT .cube / CDL / AgX',FLOOR+HERO.format(keys=anim('rotationY',-25,15)),camera=CAM.format(attrs='',keys=''),lights=LIGHTS,grade='<colorManagement workingSpace="linear-srgb" looks="grade" toneMapping="agx" exposure="0.3"><look id="grade" src="../assets/amber-teal.cube" space="srgb" mix="0.65"/></colorManagement>',notes='LUT suave dá tons âmbar e ciano; AgX controla highlights. A LUT foi criada para esta demonstração.',params='LUT mix .65 em sRGB; AgX exposure +.3; compare com 01 antes de adotar.',limits='Espaço errado da LUT muda contraste/cor. AgX altera a imagem global, incluindo títulos; não tentar recuperar luz achatada com grade.',ideas='Unificar foto e modelo; estabelecer a paleta do mundo do Short; diferenciar dois estados de uma experiência.')
(ROOT/'work/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
print('Geradas',len(catalog),'cenas')
