import build_atlas as b
from pathlib import Path
import json,math,struct,wave,shutil
import numpy as np
from PIL import Image,ImageDraw
scene=b.scene; anim=b.anim; assets=b.ASSETS; FLOOR=b.FLOOR

scene('09-deformers','A forma respira','Wave / bend / geometria 2D','''<shape id="ribbon" shape="path" x="140" y="840" width="800" height="390" path="M 0 140 C 200 -50 600 330 800 140 L 800 270 C 600 460 200 80 0 270 Z" fill="#37B9AA" stroke="#A5ECE0" strokeWidth="3">
<deform><modifier type="wave" amount="55" frequency="2" axis="x">'''+anim('phase',0,360)+'''</modifier><modifier type="bend" amount="18" axis="x"/></deform></shape>''',mats='',notes='Uma silhueta vetorial é deformada em tempo real; nenhuma sequência de imagens necessária.',params='Wave amount 55 px, frequency 2, phase 0 → 360; bend 18°. Use amplitude 10–25 para respirar, 55 para vitrine.',limits='Deformer junto de threeD em camada de imagem/vídeo é ignorado. Valores altos podem dobrar a malha sobre si mesma.',ideas='Bandeira ou membrana; objeto que reage ao calor; transformar a forma para explicar flexibilidade.')
scene('10-skeleton-skin','O gesto vem dos ossos','Skeleton / skin / três articulações','''<skeleton id="rig"><bone id="b0" x="190" y="1080" length="225"/>
<bone id="b1" parent="b0" x="225" length="225">'''+anim('rotation',-20,25)+'''</bone><bone id="b2" parent="b1" x="225" length="225">'''+anim('rotation',20,-35)+'''</bone></skeleton>
<shape id="arm" shape="rect" x="190" y="1010" width="675" height="140" radius="65" fill="#DCC189" stroke="#A58659" strokeWidth="3"><deform><modifier type="skin" skeleton="rig"/></deform></shape>''',mats='',notes='Uma faixa inteira acompanha uma cadeia de três ossos e mistura pesos entre articulações.',params='Três bones de 225 unidades; rotações moderadas -20 → 25 / 20 → -35; pesos automáticos por distância.',limits='Pesos automáticos podem dobrar partes vizinhas indesejadas. Use arquivo weights em JSON para controlar influência; IK precisa alvo e ordem válidos.',ideas='Braço mecânico; caule que cresce e aponta; personagem desenhado que acompanha uma indicação.')
scene('11-puppet-pins','Um recorte ganha vida','Puppet / pinos de posição e rigidez','''<shape id="leaf" shape="ellipse" x="310" y="680" width="460" height="760" fill="#35AFA0" stroke="#D1E8CA" strokeWidth="4"><deform><modifier type="puppet">
<pin restX="230" restY="700"/>
<pin restX="230" restY="70">'''+anim('x',-80,100)+anim('y',15,-35)+'''</pin><pin kind="starch" restX="230" restY="640" amount="3"/></modifier></deform></shape>''',mats='',notes='Base fixa e ponta móvel: o recorte se dobra mantendo sua continuidade por ARAP.',params='Pino fixo na base; deslocamento da ponta -80 → 100 px, y 15 → -35; starch amount 3 perto da base.',limits='x/y de pin são deslocamentos do restX/restY, não coordenadas absolutas. Muitos pinos aumentam o custo e podem puxar contra si.',ideas='Folha que inclina; face com respiração discreta; seta orgânica que se curva para mostrar uma força.')

floor='<shape id="ground" shape="rect" x="96" y="1480" width="888" height="28" fill="#345063"><rigidBody type="static"/></shape>'
tokens=''
for i in range(14):
    col=['#E8BC79','#48B8AD','#AACBCC'][i%3]
    tokens+=f'<shape id="token{i}" shape="ellipse" x="{230+(i%5)*128}" y="{580-(i//5)*110}" width="82" height="82" fill="{col}" stroke="#203B46" strokeWidth="3"><rigidBody shape="circle" restitution="0.26" friction="0.6" velocityX="{(i%3-1)*35}"/></shape>'
scene('12-rigid-physics','Cada ficha pesa','Rapier 2D / queda / colisão',floor+tokens,mats='',physics='<physics pixelsPerMeter="100" bounds="frame"/>',notes='Quatorze fichas caem e se apoiam num chão estático em uma execução real do motor.',params='14 corpos circle de 82 px; gravity padrão, PPM 100, restitution .26, friction .6; --parallel 1.',limits='Não prometer uma disposição final específica sem verificar a simulação. Physics cache pode fixar o resultado; renderizações seguem serial nesta produção.',ideas='Contagem que se acumula; distribuição de probabilidades como fichas; comparar massa ou atrito.')
scene('13-soft-physics','A matéria cede','Cloth / jelly / lattice',floor+'''<layer id="cloth" asset="clothAsset" x="200" y="700" boxWidth="680" boxHeight="300" fit="fill"><softBody kind="cloth" rows="8" cols="16" stiffness="180" mass="3" damping="0.25" pin="top"/></layer>
<shape id="jelly" shape="rect" x="420" y="1000" width="240" height="230" radius="45" fill="#E7B76E" stroke="#FFE0A4" strokeWidth="3"><softBody kind="jelly" rows="6" cols="6" stiffness="220" mass="3" pressure="45" damping="0.25"/></shape>'''.replace('pin="top"','pin="left"'),assets='<image id="clothAsset" src="../assets/weave.png" width="512" height="512"/>',mats='',physics='<physics pixelsPerMeter="100" bounds="frame"/>',notes='Pano preso pela borda esquerda e gel que cai: ambos deformam a própria superfície por simulação.',params='Cloth 8×16, stiffness 180, mass 3, pin left; jelly 6×6, stiffness 220, pressure 45.',limits='Molas explícitas exigem substeps; malha muito densa e stiffness alto podem ser recusados (P01). Soft colide com rigid, mas não o empurra.',ideas='Rede que cede com peso; tecido num fluxo; gel absorvendo um impacto.')
scene('14-fluid','O fluxo se encontra','Stable fluids / fontes / vorticidade','''<fluid id="flow" x="130" y="650" width="820" height="900" resolution="112" vorticity="4" buoyancy="80" dissipation="0.18" iterations="32">
<fluidSource x="250" y="760" radius="42" color="#F5BC72" density="5" velocityX="100" velocityY="-230"/>
<fluidSource x="570" y="760" radius="42" color="#49C7BB" density="5" velocityX="-100" velocityY="-230"/>
</fluid>''',mats='',still=3.25,notes='Duas fontes de dye e velocidade formam correntes que se encontram numa simulação 2D real.',params='Resolution 112, vorticity 4, buoyancy 80, iterations 32; duas fontes com cores distintas e velocityY -230.',limits='Fluido 2D estilizado, sem solver CFD validado para um experimento científico. Resolução, passos e pressão dominam CPU; cores literais.',ideas='Convecção ilustrativa; mistura entre duas correntes; explicar compressão visualmente sem fingir cálculo científico.')
scene('15-flock','A ordem é local','600 boids / separação / alinhamento','''<flock id="birds" x="130" y="680" width="820" height="850" count="600" size="5" shape="streak" color="#D8DAD2" seed="7" speed="150" maxSpeed="220" perception="65" separation="1.5" alignment="1.2" cohesion="0.8" bounds="steer"/>''',mats='',notes='Seiscentos agentes seguem regras locais; a organização nasce da simulação, não de trajetórias pré-desenhadas.',params='600 agentes, perception 65, separation 1.5, alignment 1.2, cohesion .8; seed 7.',limits='Flock representa regras abstratas; não chamar de comportamento medido de animais. Count grande pode pesar na busca de vizinhos.',ideas='Coordenação sem líder; migração ilustrada; formar uma população que se organiza.')
scene('16-slime','O caminho se reforça','Physarum / trail sensing / rede','''<slime id="net" x="130" y="700" width="820" height="820" resolution="320" agents="40000" seed="3" spawn="disc" color="#EACA87" colorLow="#17252B" speed="85" saturation="8" decay="0.1"/>''',mats='',still=3.25,notes='Agentes percebem trilhas, depositam sinal e fazem uma rede emergir. É uma execução do modelo abstrato.',params='40000 agents, resolution 320, spawn disc, speed 85, saturation 8, seed 3.',limits='Não é reprodução de um resultado biológico específico sem parâmetros/dados. Crescimento longo precisa escala temporal e evidência; CPU e checkpoints crescem.',ideas='Trilhas que se reforçam; redes sem centralização; mostrar a diferença entre explorar e consolidar.')
scene('17-erosion','O relevo guarda o fluxo','Droplet erosion / terreno procedural','''<erosion id="land" x="130" y="680" width="820" height="900" resolution="192" droplets="16000" seed="5" relief="1.8" sunAzimuth="315" colorLow="#244952" colorHigh="#DFC58D"/>''',mats='',notes='Gotas transportam e depositam sedimento sobre um terreno procedural; a imagem é o hillshade do estado simulado.',params='Resolution 192, droplets 16000/s, relief 1.8, seed 5; aumentar resolução só após medir.',limits='Terreno sintético sem geografia real nem escala de tempo física. Poucos segundos mudam detalhes; amplie um trecho para mostrar antes/depois.',ideas='Explicar erosão e depósito; revelar caminhos na paisagem; usar terreno como metáfora de memória.')

# Synthetic Gaussian splats in the native .splat format; no borrowed scan.
with (assets/'cloud.splat').open('wb') as f:
    rng=np.random.default_rng(18)
    for i in range(6000):
        a=rng.uniform(0,2*math.pi); elevation=rng.normal(0,.16); radius=rng.normal(2,.15)
        p=[radius*math.cos(a),elevation,radius*math.sin(a)]
        size=rng.uniform(.025,.07)
        color=[int(120+80*(math.sin(a)*.5+.5)),190,180,155]
        f.write(struct.pack('<6f8B',*p,size,size,size,*color,255,128,128,128))
scene('18-gaussian-splats','Um objeto de pontos','Gaussian splats / asset sintético',FLOOR+'''<object3D id="cloud" primitive="mesh" mesh="splatAsset" x="540" y="1040" z="100" scaleX="1.7" scaleY="1.7" scaleZ="1.7" rotationX="60">'''+anim('rotationY',0,70)+'''</object3D>''',assets='<mesh id="splatAsset" src="../assets/cloud.splat" format="splat"/>',camera=b.CAM.format(attrs='',keys=''),lights=b.LIGHTS,notes='Seis mil gaussianas formam um anel volumétrico que gira. O asset é sintético e não simula um scan real.',params='6000 splats; scale 1.7; rotationY 0 → 70. Para captura: mesh format ply com f_dc/scale, câmera e escala conferidas.',limits='Splats não recebem nova luz nem projetam sombras. .splat não tem spherical harmonics; captura PLY pode trazer brilho dependente da vista.',ideas='Trazer um artefato capturado para um Short; mostrar uma nuvem volumétrica; comparar captura e reconstrução.')
path='M 170 1280 C 220 650 820 650 900 1280'
scene('19-motion-path','O movimento tem caminho','SVG path / constant speed / autoOrient',f'''<shape id="route" shape="path" width="1080" height="1600" path="{path}" fill="#00000000" stroke="#436B7D" strokeWidth="5"/>
<shape id="vehicle" shape="path" width="100" height="68" path="M 0 0 L 100 34 L 0 68 L 20 34 Z" fill="#EBC282" anchorX="50" anchorY="34"><motionPath path="{path}" start="0" end="3.5" constantSpeed="true" autoOrient="true"/></shape>''',mats='',notes='A seta percorre a curva com orientação da tangente e distância uniforme por segundo.',params='SVG cubic path, constantSpeed true, autoOrient true; 3.5 s.',limits='Path é coordenada do pai. Orientação pode virar em cúspides; escolha trajeto suave ou remova autoOrient. Rota ilustrativa, sem dado geográfico.',ideas='Percurso de um sinal; material entrando numa máquina; uma rota com posição sincronizada à fala.')
text_assets=''
text_body=''
for i,(text,preset) in enumerate([('REVELAR','mask-reveal'),('DESCOBRIR','scramble'),('2 048','counter')]):
    text_assets+=f'<text id="word{i}" text="{text}" fontFile="../assets/atlas.ttf" size="88" weight="700" color="{["#E9CA8E","#5ED6C0","#D5E3E4"][i]}" width="888" height="130"/>'
    text_body+=f'<layer id="wordLayer{i}" asset="word{i}" x="96" y="{700+i*260}"><textAnimator preset="{preset}" presetStart="0.1" presetDuration="1.8"/></layer>'
scene('20-text-animators','A palavra também age','Mask reveal / scramble / counter',text_body,assets=text_assets,mats='',still=2.75,notes='Três presets com funções distintas: revelar, resolver letras, contar um número com layout tipográfico.',params='PresetStart .1, presetDuration 1.8; segurar palavra completa por pelo menos 1.5 s.',limits='Counter interpola números: não usar como contagem real de simulação. Scramble só para revelação, não para informação que precisa ler antes de estabilizar.',ideas='Um termo que emerge de uma forma; descobrir uma sequência; um número que chega ao resultado verdadeiro da narração.')

transitions=''
for i,kind in enumerate(['light-leak','whip-pan','luma']):
    yy=630+i*300
    transitions+=f'<group id="row{i}" x="130" y="{yy}" width="820" height="230">'
    transitions+=f'<shape id="a{i}" shape="rect" width="820" height="230" fill="#24505B" end="1.75"/><shape id="b{i}" shape="rect" width="820" height="230" fill="#D8BB81" start="1.75"/>'
    if kind=='luma':
        transitions+=f'<layer id="matte{i}" asset="lumaAsset"/>'
    transitions+=f'<transition type="{kind}" from="a{i}" to="b{i}" duration="0.85" direction="right" '+(f'matte="matte{i}"' if kind=='luma' else '')+'/></group>'
scene('21-motivated-transitions','Mudar tem uma razão','Light leak / whip pan / luma',transitions,assets='<generator id="lumaAsset" kind="gradient" width="820" height="230" paint="#000000" paint2="#FFFFFF"/>',mats='',still=1.6,notes='Três janelas com a mesma mudança de estado: memória/luz, deslocamento e revelação por luminância.',params='Duração .85 s centrada em 1.75; whip-pan direction right; luma exige matte node.',limits='Whip-pan é warp 2D, não câmera 3D. Matte nomeia nó, não asset. Em filmes, escolha uma transição pelo sentido da mudança e reveja os frames intermediários.',ideas='Luz que abre um flashback; deslocamento rápido entre duas regiões do mesmo aparelho; revelar segundo estado por sua luminância.')

rate=48000; n=int(3.5*rate); t=np.arange(n)/rate; sound=np.zeros(n)
for pos in [.25,1,1.75,2.5,3.1]:
    age=t-pos; sound+=np.where(age>=0,.22*np.exp(-np.maximum(age,0)*16)*np.sin(2*np.pi*(145*age+45*age*age)),0)
with wave.open(str(assets/'pulse.wav'),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes((np.clip(sound,-1,1)*32767).astype('<i2').tobytes())
scene('22-audio-reactive','O som move a imagem','audioAmplitude / link / análise do mix','''<shape id="pulse" shape="ellipse" x="540" y="1060" width="580" height="580" anchorX="290" anchorY="290" fill="#3DC1AD" stroke="#D6E4D2" strokeWidth="4"><link property="scaleX" source="audio:drum:low" scale="0.5" offset="0.75"/><link property="scaleY" source="audio:drum:low" scale="0.5" offset="0.75"/></shape>''',assets='<audio id="pulseAsset" src="../assets/pulse.wav" duration="3.5" sampleRate="48000" channels="1"/>',mats='',audio='<audioMix sampleRate="48000"><audioTrack id="drum" asset="pulseAsset" volume="0.8"/></audioMix>',notes='O círculo lê o envelope low da trilha realmente misturada na entrega. Pulso original gerado para a demonstração.',params='link audio:drum:low, scale .5, offset .75; som com cinco ataques a .25 / 1 / 1.75 / 2.5 / 3.1 s.',limits='render isolado não prepara análise de áudio. O still deste recurso deve vir do encode. Não há avaliação de escuta nesta sessão; som da vitrine precisa playback.',ideas='Pulso no componente que faz o som; espectro ligado à onda falada; reagir a batidas sem marcar cada key à mão.')

if not (assets/'synthetic-hill.pmtiles').exists():
    shutil.copy('/home/pals/src/rs-scene-render/crates/sr-geo/tests/fixtures/hill.pmtiles',assets/'synthetic-hill.pmtiles')
toy={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'ILHA SINTÉTICA'},'geometry':{'type':'Polygon','coordinates':[[[-.1,-.1],[.1,-.1],[.1,.1],[-.1,.1],[-.1,-.1]]]}}]}
(assets/'toy-island.geojson').write_text(json.dumps(toy))
scene('23-native-map-relief','O mapa tem relevo','Map nativo / Terrarium / terreno sintético',FLOOR+'''<object3D id="terrain" primitive="map" map="terrainMap" terrain="dem" exaggeration="4" resolution="96" textureSize="768" x="540" y="1080" z="50" rotationX="-65">'''+anim('rotationY',-12,12)+'''</object3D>''',camera=b.CAM.format(attrs='',keys='').replace('z="-1400"','z="-1100"'),lights=b.LIGHTS.replace('intensity="450"','intensity="130"').replace('intensity="330"','intensity="80"').replace('contactShadows="true"','contactShadows="false"'),assets='''<geo id="island" src="../assets/toy-island.geojson"/>
<tiles id="dem" src="../assets/synthetic-hill.pmtiles" attribution="Elevação sintética de teste rs-scene-render"/>
<map id="terrainMap" width="820" height="820" projection="web-mercator" centerLon="0" centerLat="0" zoom="12" background="#58AFA3"><geoLayer geo="island" fill="#9BC6AC" stroke="#E8D19C" strokeWidth="4"/><route points="-0.06,-0.04 0.06,0.04" stroke="#E8C27E" strokeWidth="8"/><pin lon="0" lat="0" radius="10"/></map>''',notes='Um map asset é drapeado num mesh, elevado por tiles Terrarium e iluminado no renderer 3D. O exagero vertical de 4× torna a encosta legível nesta demonstração.',params='Web Mercator zoom12, terrain DEM, resolution96, texture768, exaggeration4; tilt -65°; câmera z -1100.',limits='Este exemplo é uma ilha e elevação sintéticas, sem localização factual. Terrain precisa Web Mercator. Dados reais exigem licença/crédito e exagero declarado; globe ainda não tem terrain. Contact shadows desligadas no plano; shadow maps preservados.',ideas='Mostrar um trajeto sobre a encosta; comparar relevo e caminho; aproximar da região que altera uma decisão.')
scene('24-animated-charts','O dado ocupa a tela','Chart / progress / valores de demonstração','''<layer id="bars" asset="barChart" x="130" y="700"/>
<layer id="curve" asset="lineChart" x="130" y="1170"/>''',assets='''<chart id="barChart" kind="column" width="820" height="360" labels="A,B,C,D" showAxes="true" showValues="true"><series name="Demo" values="12 24 48 72" color="#42BEAC"/>'''+anim('progress',0,1,.1,2.8)+'''</chart>
<chart id="lineChart" kind="line" width="820" height="320" labels="0,1,2,3,4" showAxes="true"><series name="Demo" values="2 5 9 16 26" color="#E3BD7D"/>'''+anim('progress',0,1,.1,2.8)+'</chart>',mats='',still=3,notes='As barras e a curva são dados nativos, revelados por progress. Valores sintéticos para ensino de layout.',params='progress 0 → 1 em 2.7 s; showAxes true, showValues true para barras; largura820.',limits='Animação draw-on não é crescimento observado. Identificar unidade/escala e fonte no filme; labels do gráfico não têm collision pass avançado.',ideas='Diferença entre cenários; uma curva como objeto central do Short; comparação antes/depois sincronizada à frase.')
shader='''vec4 effect(vec2 uv) {
 vec2 p=(uv-vec2(0.5))*vec2(1.0,1.15);
 float accum=0.0;
 for(int i=0;i<24;i++) {
  float z=float(i)/24.0;
  vec2 q=p*(0.8+z*0.5);
  float f=sin(q.x*9.0+z*5.0+iTime)*cos(q.y*7.0-z*6.0+iTime*0.7);
  accum+=exp(-7.0*length(q))*max(0.0,f)*0.055;
 }
 vec3 c=vec3(0.025,0.055,0.075)+accum*vec3(0.4,1.1,0.9);
 return vec4(c,1.0);
}
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
 fragColor=effect(fragCoord/iResolution.xy);
}'''
(assets/'volume.glsl').write_text(shader)
scene('25-glsl-volume','Um volume desenhado','GLSL / integração estilizada / tempo','''<shape id="volume" shape="rect" x="130" y="660" width="820" height="920" fill="#000000" effects="volumeFX"/>''',mats='',effects='<effect id="volumeFX" type="shader" src="../assets/volume.glsl"/>',notes='Shader integra 24 camadas de densidade para uma aparência de volume animado, num único quad.',params='24 passos; iTime no sin/cos; gradação ciano sutil; superfície820×920.',limits='Volume estilizado, sem física de transporte de luz e sem interação com luzes PBR. GLSL inválido pode passar input: sempre exigir --strict.',ideas='Campo invisível mostrado como ilustração; turbulência como fundo localizado; mostrar a zona ativa de um fenômeno.')

scene('26-rich-2d-count','A quantidade é a imagem','96 peças / repetição nativa / câmera 2.5D','''<layer id="field" asset="richField"/>
<group id="board" width="820" height="1000" x="130" y="610" effects="contactFX">
<shape id="panel" shape="rect" width="820" height="1000" radius="26" fill="#213B47" stroke="#78939A" strokeWidth="3" threeD="true" zDepth="0"/>
<layer id="countLabel" asset="countAsset" x="40" y="48" threeD="true" zDepth="0"/>
<repeat id="rows" count="12" x="38" y="220" offsetY="62">
<shape id="cell" shape="rect" width="70" height="45" radius="6" fill="#D8C496" stroke="#96825F" strokeWidth="1.5" threeD="true" zDepth="0"><shapeModifier type="repeater" copies="8" offsetX="96"/></shape>
</repeat>
<shape id="chosen" shape="rect" x="38" y="220" width="70" height="45" radius="6" fill="#3BBBA9" stroke="#B7EEE1" strokeWidth="6" threeD="true" zDepth="0"/>
</group>''',assets='''<generator id="richField" kind="solid" width="1080" height="1920" paint="url(#richGlow)"/>
<text id="countAsset" text="96 PEÇAS" fontFile="../assets/atlas.ttf" size="80" color="#F2E5C6" width="740" height="120"/>''',paints='<paints><radialGradient id="richGlow" cx="0.5" cy="0.56" r="0.68" aspect="0.68"><stop offset="0" color="#243C49"/><stop offset="1" color="#0B1520"/></radialGradient></paints>',camera='<camera id="cam" x="540" y="960" z="-1500" fov="42">'+anim('z',-1500,-1407)+'</camera>',mats='',effects='<effect id="contactFX" type="drop-shadow" radius="12" offsetY="12" color="#00000070"/>',notes='A imagem contém exatamente 12×8=96 peças. Um shapeModifier repeater cria cada fila; repeat cria as 12 filas. A peça escolhida é recolorida por uma cobertura coincidente, sem adicionar uma peça à contagem visível.',params='8 copies ×12 rows; traços 1.5 /3 /6 px; luz radial; drop-shadow radius12 offsetY12; câmera real z -1500 → -1407.',limits='A contagem é demonstrativa, não dado de uma pesquisa. A cobertura escolhida coincide com a primeira peça. O plano único usa 2.5D apenas para câmera real; nenhum efeito 3D é necessário para enriquecer a informação.',ideas='Mostrar N casos de verdade; selecionar um item sem perder a população; aproximar do detalhe e voltar à totalidade mantendo o mesmo objeto.')

(b.ROOT/'work/catalog.json').write_text(json.dumps(b.catalog,ensure_ascii=False,indent=2))
print('Atlas agora:',len(b.catalog),'cenas')
