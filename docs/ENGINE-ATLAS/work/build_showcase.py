from pathlib import Path
import math,json,copy,xml.etree.ElementTree as ET
import numpy as np
root=Path(__file__).resolve().parents[1];assets=root/'assets'
catalog=json.loads((root/'work/catalog.json').read_text())
template=ET.parse(root/'26-rich-2d-count/scene.xml').getroot()

def mesh(name,vertices,faces):
    # Authored in scene units, Y down; OBJ has Y up and metres.
    lines=[f'v {x/100:.7f} {-y/100:.7f} {-z/100:.7f}' for x,y,z in vertices]
    xs=[p[0] for p in vertices];zs=[p[2] for p in vertices];xmin,xmax=min(xs),max(xs);zmin,zmax=min(zs),max(zs)
    lines += [f'vt {(x-xmin)/max(1,xmax-xmin):.7f} {(z-zmin)/max(1,zmax-zmin):.7f}' for x,y,z in vertices]
    # A 180-degree rotation around X preserves handedness and winding.
    lines+=['f '+' '.join(str(i+1)+'/'+str(i+1) for i in face) for face in faces]
    (assets/(name+'.obj')).write_text('\n'.join(lines)+'\n')

def lathe(name,profile,n=96):
    v=[];f=[]
    for r,y in profile:
        v.extend([(r*math.cos(a*2*math.pi/n),y,r*math.sin(a*2*math.pi/n)) for a in range(n)])
    for j in range(len(profile)-1):
        for k in range(n):
            a=j*n+k;b=j*n+(k+1)%n;c=(j+1)*n+(k+1)%n;d=(j+1)*n+k;f.extend([(a,b,c),(a,c,d)])
    mesh(name,v,f)

# Gear with a true centre hole and bevelled teeth, 24 teeth × four vertices.
n=192;v=[];f=[]
for z,rbase in [(-45,205),(-35,220),(35,220),(45,205)]:
    for k in range(n):
        r=rbase+(22 if k%8 in [2,3,4,5] else 0);a=k*2*math.pi/n;v.append((r*math.cos(a),r*math.sin(a),z))
for z in [-45,45]:
    for k in range(n):
        a=k*2*math.pi/n;v.append((72*math.cos(a),72*math.sin(a),z))
for j in range(3):
    for k in range(n):a=j*n+k;b=j*n+(k+1)%n;c=(j+1)*n+(k+1)%n;d=(j+1)*n+k;f.extend([(a,b,c),(a,c,d)])
for k in range(n):
    j=(k+1)%n;f.extend([(k,4*n+k,4*n+j),(k,4*n+j,j),(3*n+k,3*n+j,5*n+j),(3*n+k,5*n+j,5*n+k),(4*n+k,5*n+k,5*n+j),(4*n+k,5*n+j,4*n+j)])
mesh('gear',v,f)
lathe('cup',[(0,0),(99,0),(108,-8),(114,-330),(110,-346),(102,-346),(100,-326),(93,-16),(0,-16)])
lathe('kettle',[(0,0),(155,0),(190,-30),(220,-120),(220,-200),(195,-290),(145,-345),(112,-355),(112,-372),(0,-372)])
lathe('pawn',[(0,0),(6,0),(7,-2),(6,-4),(3,-6),(2,-17),(4,-19),(5,-23),(4,-27),(0,-28)],64)
lathe('rook',[(0,0),(6,0),(7,-2),(6,-4),(4,-7),(4,-23),(7,-23),(7,-28),(0,-28)],64)
# Folded paper: three planar strips, thickened into a closed solid.
v=[(-185,0,-140),(-55,-80,-140),(65,0,-140),(185,-24,-140),(-185,0,140),(-55,-80,140),(65,0,140),(185,-24,140)]
v+= [(x,y+2,z) for x,y,z in v];f=[]
for k in range(3): f.extend([(k,k+1,k+5),(k,k+5,k+4),(k+8,k+12,k+13),(k+8,k+13,k+9)])
for k in range(3): f.extend([(k,k+8,k+9,k+1),(k+4,k+5,k+13,k+12)])
f.extend([(0,4,12,8),(3,11,15,7)]);mesh('folded-paper',v,f)
# Spoon has a shallow elliptical bowl and a tapered curved handle.
v=[];f=[];nr=14;nt=72
for j in range(nr+1):
    r=j/nr
    for k in range(nt):
        a=k*2*math.pi/nt;v.append((65*r*math.cos(a),-8-25*r*r,85*r*math.sin(a)-80))
for j in range(nr):
    for k in range(nt):a=j*nt+k;b=j*nt+(k+1)%nt;c=(j+1)*nt+(k+1)%nt;d=(j+1)*nt+k;f.extend([(a,b,c),(a,c,d)])
base=len(v)
for j in range(42):
    z=j*7;w=14+10*(j/41)**4;y=-30-8*math.sin(j/41*math.pi);v.extend([(-w,y,z),(w,y,z)])
for j in range(41):a=base+j*2;f.extend([(a,a+1,a+3),(a,a+3,a+2)])
mesh('spoon',v,f)
v=[];f=[];nx=48;ny=48
for j in range(ny+1):
    z=(j/ny-.5)*350
    for i in range(nx+1):
        x=(i/nx-.5)*360;height=130*math.exp(-((x/95)**4+(z/100)**4));y=-height-8-8*math.sin(x/15)*math.cos(z/27);v.append((x,y,z))
for j in range(ny):
    for i in range(nx):a=j*(nx+1)+i;b=a+1;c=b+nx+1;d=a+nx+1;f.extend([(a,b,c),(a,c,d)])
mesh('draped-cloth',v,f)

MATS='''<material id="floorMat" baseColor="#141C20" roughness="0.55"/>
<material id="steel" baseColor="#BBCBD3" metallic="1" roughness="0.24" doubleSided="true"/>
<material id="brass" baseColor="#C99848" metallic="1" roughness="0.22"/>
<material id="glass" baseColor="#E6F7F5" transmission="1" roughness="0.025" ior="1.48" thickness="8" attenuationColor="#8ACEC2" attenuationDistance="450"/>
<material id="water" baseColor="#C6E9EF" transmission="1" roughness="0.03" ior="1.33" thickness="100" attenuationColor="#428F9D" attenuationDistance="250"/>
<material id="paper" baseColor="#EFE0BF" baseColorMap="../assets/paper.png" roughness="0.96" doubleSided="true"/>
<material id="cloth" baseColor="#407E83" baseColorMap="../assets/weave.png" roughness="0.9" sheenColor="#AED6C9" sheenRoughness="0.5" doubleSided="true"/>
<material id="black" baseColor="#070B10" roughness="0.12"/>
<material id="ivory" baseColor="#ECE0BF" roughness="0.45"/><material id="teal" baseColor="#32A89B" roughness="0.3" clearcoat="0.25"/>'''
CAM='<camera id="cam" x="540" y="450" z="-1050" pitch="-35" fov="42" far="100000" ambientOcclusion="true" aoRadius="35" aoIntensity="1.25"/>'
FLOOR='<object3D id="floor" primitive="box" width="200000" height="30" depth="200000" x="540" y="1440" z="0" material="floorMat" castShadow="false"/>'
LIGHTS='''<light id="ambient" type="ambient" intensity="0.07" color="#B7C8D4"/>
<light id="key" type="point" x="-200" y="400" z="-600" intensity="200" colorTemperature="4300" castShadow="true" shadowMapSize="2048" shadowSoftness="1.5" contactShadows="false"/>
<light id="rim" type="point" x="950" y="700" z="600" intensity="650" color="#72CFE4"/>
<light id="dome" type="dome" environment="../assets/studio.hdr" intensity="0.32"/>'''
def anim(prop,a,b):return f'<animate property="{prop}"><key time="0" value="{a}" interpolation="sine-in-out"/><key time="3.5" value="{b}"/></animate>'
def write(slug,title,sub,body,camera=CAM,lights=LIGHTS,mats=MATS,grade='',extra_assets='',effects=''):
    scene=copy.deepcopy(template)
    for tag in ['assets','paints','materials','composition','lights','effects','colorManagement']:
        old=scene.find(tag)
        if old is not None: scene.remove(old)
    assetsnode=ET.fromstring(f'''<assets><font id="pn-archivo" src="../assets/archivo.ttf" family="Archivo" weight="400" license="OFL-1.1"/>
<text id="titleAsset" text="{title.upper()}" style="pn-heading" fontFile="../assets/archivo.ttf" size="64" weight="700" color="#F4EFE4" width="888" height="180"/>
<text id="subAsset" text="{sub}" style="pn-subtitle" fontFile="../assets/archivo.ttf" size="36" color="#A8BCCB" width="888" height="130"/>
<text id="footAsset" text="PALS / ENGINE ATLAS" fontFile="../assets/archivo.ttf" size="23" color="#A8BCCB" width="888" height="50"/>{extra_assets}</assets>''')
    scene.append(assetsnode)
    if mats:scene.append(ET.fromstring('<materials>'+mats+'</materials>'))
    composition=ET.fromstring('<composition>'+camera+body+'''<layer id="title" asset="titleAsset" x="96" y="205"/><shape id="rule" shape="rect" x="96" y="400" width="94" height="5" fill="#E8BC79"/><layer id="sub" asset="subAsset" x="96" y="440"/><layer id="footer" asset="footAsset" x="96" y="1720"/></composition>''')
    scene.append(composition)
    if lights:scene.append(ET.fromstring('<lights>'+lights+'</lights>'))
    if effects:scene.append(ET.fromstring('<effects>'+effects+'</effects>'))
    if grade: scene.insert(2,ET.fromstring(grade))
    tree=ET.ElementTree(scene);ET.indent(tree);tree.write(root/slug/'scene.xml',encoding='utf-8',xml_declaration=True)
    for item in catalog:
        if item['slug']==slug:
            item['title']=title;item['notes']+=' Vitrine revisada: Archivo, subtítulo36, assunto próprio e piso sem borda no enquadramento.'

gear_asset='<mesh id="gearAsset" src="../assets/gear.obj" format="obj"/>'
write('01-pbr-key-rim','A luz revela os dentes','Engrenagem / key lateral / rim frio',FLOOR+'<object3D id="gear" primitive="mesh" mesh="gearAsset" x="540" y="1183" z="0" material="steel" rotationY="-12">'+anim('rotationY',-20,12)+'</object3D>',extra_assets=gear_asset)
# DOF on chess pieces: close optics in scene units (100 units = 1 metre).
dofcam='<camera id="cam" x="540" y="960" z="-300" pitch="-35" focalLength="50" depthOfField="true" fStop="2.2" focusDistance="52" far="100000">'+anim('focusDistance',52,325)+'</camera>'
doflights='''<light id="ambient" type="ambient" intensity="0.15"/><light id="key" type="point" x="515" y="900" z="-330" intensity="0.8" colorTemperature="4500" castShadow="true" shadowMapSize="1024"/><light id="dome" type="dome" environment="../assets/studio.hdr" intensity="0.4"/>'''
dofbody='<object3D id="table" primitive="box" width="200000" height="4" depth="200000" x="540" y="1172" z="0" material="floorMat" castShadow="false"/>'
for ident,kind,x,z,sc,mat in [('near','rook',532,-265,.35,'teal'),('middle','pawn',545,-205,.7,'ivory'),('far','pawn',606,-40,1.6,'brass')]:
    base=960+math.tan(math.radians(35))*(z+300)+20
    h=1170-base
    dofbody+=f'<object3D id="{ident}Stand" primitive="box" width="{sc*20}" height="{h}" depth="{sc*20}" x="{x}" y="{base+h/2}" z="{z}" material="floorMat"/>'
    dofbody+=f'<object3D id="{ident}" primitive="mesh" mesh="{kind}Asset" x="{x}" y="{base}" z="{z}" scaleX="{sc}" scaleY="{sc}" scaleZ="{sc}" material="{mat}"/>'
write('03-dof-focus-pull','O foco escolhe a peça','Óptica de perto / foco 52 → 325 cm',dofbody,camera=dofcam,lights=doflights,extra_assets='<mesh id="rookAsset" src="../assets/rook.obj" format="obj"/><mesh id="pawnAsset" src="../assets/pawn.obj" format="obj"/>')
materialbody=FLOOR
for ident,name,x,z,mat in [('spoon','spoon',290,-230,'steel'),('cup','cup',775,300,'glass'),('fold','folded-paper',285,300,'paper'),('drape','draped-cloth',740,-230,'cloth')]:
    materialbody+=f'<object3D id="{ident}" primitive="mesh" mesh="{name}Asset" x="{x}" y="1424" z="{z}" material="{mat}"/>'
materialbody+='<object3D id="waterBody" primitive="cylinder" radius="94" height="150" segments="96" x="775" y="1349" z="300" material="water"/>'
ma=''.join(f'<mesh id="{name}Asset" src="../assets/{name}.obj" format="obj"/>' for name in ['spoon','cup','folded-paper','draped-cloth'])
write('06-materials','Quatro maneiras de tocar','Metal / vidro e água / papel / tecido',materialbody,extra_assets=ma,lights=LIGHTS.replace('intensity="650"','intensity="160"').replace('intensity="0.32"','intensity="0.9"').replace('intensity="0.07"','intensity="0.15"'),mats=MATS.replace('baseColor="#141C20"','baseColor="#4C5C5D"'))
# Optical barrel, glass front and separate rings give a recognisable lens.
lens=FLOOR+'<object3D id="barrel" primitive="cylinder" radius="170" height="270" segments="96" x="540" y="1252" z="0" rotationX="90" material="steel"/>'
for i,z in enumerate([-130,-60,30,110]): lens+=f'<object3D id="ring{i}" primitive="torus" radius="166" height="15" segments="96" x="540" y="1252" z="{z}" rotationX="90" material="brass"/>'
lens+='<object3D id="lens" primitive="cylinder" radius="149" height="12" segments="96" x="540" y="1252" z="-145" rotationX="90" material="teal"/><object3D id="iris" primitive="cylinder" radius="45" height="8" segments="96" x="540" y="1252" z="-155" rotationX="90" material="black"/>'
write('08-grade-lut-look','O look muda a leitura','Óptica / antes e depois do LUT',lens,grade='<colorManagement workingSpace="linear-srgb" toneMapping="agx" exposure="0.3" looks="grade"><look id="grade" src="../assets/showcase-amber-teal.cube" space="srgb" mix="1"/></colorManagement>')
for item in catalog:
    if item['slug']=='01-pbr-key-rim': item['params']='Engrenagem OBJ original; key200 lateral, rim650 por trás, dome .32; piso200000; shadow2048, contato desligado. A/B isola rim.'
    if item['slug']=='03-dof-focus-pull': item['params']='50mm, f/2.2, focus52→325 unidades (0.52→3.25m); três peças em profundidades físicas distintas, pedestais sobre a mesa. 100 unidades=1m.';item['limits']='DOF apenas object3D. A cena usa escala próxima da lente para círculo de confusão claramente visível; peças traseiras recebem escala maior para comparação de foco.'
    if item['slug']=='06-materials': item['params']='Colher OBJ, copo oco com parede8, água IOR1.33, folha dobrada e pano drapejado; todos na mesa y1425. Vidro IOR1.48, roughness .025.';item['limits']='Água e pano são geometrias estáticas ilustrativas; não são fluidos/soft-body neste exemplo. Refração screen-space não tem cáusticas. Textura das fibras não simula microestrutura.'
    if item['slug']=='08-grade-lut-look': item['params']='LUT .cube17³ mix1, working linear-srgb, AgX exposure.3; comparação com a mesma cena sem LUT.'
(root/'work/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
print('Vitrine 01/03/06/08 gerada',flush=True)
