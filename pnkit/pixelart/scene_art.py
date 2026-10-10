"""Low-resolution adventure scene. Every visible mark is native pixel geometry."""
from .geometry import Geometry
import math, random

P={
 'ink':'#1d2028','black':'#13191e','deep':'#292b32','purple':'#3d343c',
 'umber':'#4d3c36','brown':'#63483e','brick':'#7d5544','clay':'#98684b',
 'ochre':'#b58358','sand':'#cfa576','cream':'#e0c292','ivory':'#efdab0',
 'plaster0':'#65564e','plaster1':'#827361','plaster2':'#a99476',
 'plaster3':'#bead8b','wood0':'#39302c','wood1':'#684d34','wood2':'#947047',
 'wood3':'#bf9158','metal0':'#22373b','metal1':'#36534f','metal2':'#527166',
 'metal3':'#819384','metal4':'#b5b79b','steel0':'#3d4b4d','steel1':'#68797a',
 'steel2':'#9fa7a0','steel3':'#d4d2b6','blue0':'#253c53','blue1':'#3b6277',
 'blue2':'#698d9b','blue3':'#a0b9b8','red0':'#652e2d','red1':'#a34a32',
 'red2':'#d27848','gold':'#e9b55f','skin0':'#92583f','skin1':'#c18a56',
 'skin2':'#e5b375','skin3':'#f5d293','hair':'#302a27','trouser0':'#343e43',
 'trouser1':'#58635f','trouser2':'#8b9080','floor0':'#594839','floor1':'#786044',
 'floor2':'#95774f','floor3':'#b49466','glass0':'#51675f','glass1':'#8f9f87',
 'glass2':'#c6c7a0','green':'#53724b'}

def r(g,x,y,w,h,c):return g.rect(x,y,w,h,P.get(c,c))
def poly(g,pts,c):return g.poly(pts,P.get(c,c))
def line(g,a,b,w,c):return g.line(a,b,w,P.get(c,c))
def ellipse(g,x,y,rx,ry,c):return g.ellipse(x,y,rx,ry,P.get(c,c))

# Five-by-seven glyphs. Type uses the same logical pixel grid as the artwork.
FONT={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01110'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['111','010','010','010','010','010','111'],
'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','11001','10101','10011','10011','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','11011','10001'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10001','10011','10101','11001','10001','01110'],
'1':['010','110','010','010','010','010','111'],
'2':['01110','10001','00001','00010','00100','01000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
'-':['000','000','000','111','000','000','000'],
'.':['0','0','0','0','0','1','1'],',':['00','00','00','00','01','01','10'],
':':['0','1','1','0','1','1','0'],
'?':['01110','10001','00001','00010','00100','00000','00100'],' ':['000']*7}

def lettering(text,color='ivory'):
 import unicodedata
 g=Geometry();x=0
 for raw in text.upper():
  base=unicodedata.normalize('NFD',raw);ch=base[0];glyph=FONT.get(ch,FONT[' '])
  for yy,row in enumerate(glyph):
   for xx,bit in enumerate(row):
    if bit=='1':r(g,x+xx,yy,1,1,color)
  if '\u0301' in base:r(g,x+3,-2,1,1,color);r(g,x+2,-1,1,1,color)
  if '\u0303' in base:r(g,x+1,-2,2,1,color);r(g,x+3,-1,2,1,color)
  if '\u0302' in base:r(g,x+2,-2,1,1,color);r(g,x+1,-1,1,1,color);r(g,x+3,-1,1,1,color)
  if '\u0300' in base:r(g,x+1,-2,1,1,color);r(g,x+2,-1,1,1,color)
  if '\u0327' in base:r(g,x+2,7,1,1,color);r(g,x+1,8,1,1,color)
  x+=len(glyph[0])+1
 return g,x-1

def plank(g,x,y,w,h):
 r(g,x,y,w,h,'wood1');r(g,x,y,w,1,'wood3');r(g,x,y+h-1,w,1,'wood0')
 for z in range(x+3,x+w-3,8):r(g,z,y+2,4,1,'wood2')
 return g

def crate(w=26,h=20):
 g=Geometry();r(g,0,0,w,h,'wood0');r(g,1,1,w-2,h-2,'wood1')
 for y in range(2,h-2,4):plank(g,1,y,w-2,4)
 for x in [2,w-5]:r(g,x,0,3,h,'wood2');r(g,x,0,1,h,'wood3')
 line(g,(4,h-3),(w-4,3),1,'wood2');r(g,3,2,1,1,'metal4');r(g,w-4,h-3,1,1,'metal4')
 return g

def barrel(w=18,h=25,color='wood1'):
 g=Geometry();poly(g,[(3,1),(w-3,1),(w,5),(w,h-4),(w-3,h),(3,h),(0,h-4),(0,5)],color)
 for x in range(3,w-2,4):r(g,x,4,1,h-6,'wood0');r(g,x+1,4,1,h-6,'wood2')
 for y in [5,h-7]:r(g,0,y,w,3,'steel0');r(g,0,y,w,1,'steel1')
 ellipse(g,w/2,2,w/2-1,2,'wood3');ellipse(g,w/2,2,w/2-3,1,'wood0')
 return g

def cog(radius=8,phase=0):
 g=Geometry();ellipse(g,0,0,radius,radius,'steel0');ellipse(g,0,0,radius-1,radius-1,'steel1')
 for i in range(8):
  a=i*math.pi/4+phase;dx,dy=math.cos(a),math.sin(a)
  line(g,(dx*(radius-2),dy*(radius-2)),(dx*(radius+1),dy*(radius+1)),1,'steel1')
 ellipse(g,0,0,radius-3,radius-3,'metal0')
 for i in range(4):
  a=i*math.pi/2+phase;line(g,(0,0),((radius-4)*math.cos(a),(radius-4)*math.sin(a)),.65,'steel2')
 ellipse(g,0,0,2,2,'steel3');r(g,0,0,1,1,'steel0')
 return g

def shelf(g,x,y,w,h):
 r(g,x,y,w,h,'umber');r(g,x+2,y+2,w-4,h-3,'wood0')
 for yy in range(y+13,y+h,17):
  plank(g,x-2,yy,w+4,3)
 for xx in [x,x+w-3]:r(g,xx,y,3,h,'wood1');r(g,xx,y,1,h,'wood3')
 rng=random.Random(36)
 for yy in range(y+13,y+h,17):
  xx=x+4
  while xx<x+w-7:
   ww=rng.randrange(5,11);hh=rng.randrange(6,12);c=rng.choice(['clay','metal1','plaster1','red0'])
   r(g,xx,yy-hh,ww,hh,c);r(g,xx,yy-hh,ww,1,'sand');r(g,xx+ww-2,yy-hh+1,2,hh-1,'umber')
   if rng.random()<.55:r(g,xx+2,yy-hh+3,ww-5,3,'plaster3')
   xx+=ww+2

def background():
 g=Geometry();rng=random.Random(1952)
 r(g,0,0,320,180,'plaster1')
 poly(g,[(0,0),(320,0),(320,24),(0,45)],'umber')
 poly(g,[(0,29),(135,25),(136,114),(0,128)],'brick')
 # Worn brick wall; selected clusters keep noise out of quiet areas.
 for yy in range(26,130,5):
  for xx in range(-8+(yy//5%2)*8,142,17):
   w=rng.choice([14,15,16]);r(g,xx,yy,w,4,rng.choice(['brick','brick','clay','brown']))
   if rng.random()<.5:r(g,xx+1,yy,w-2,1,'ochre')
 poly(g,[(0,51),(24,50),(31,92),(26,122),(0,128)],'plaster1')
 poly(g,[(0,52),(20,52),(23,73),(29,91),(22,104),(25,121),(0,125)],'plaster2')
 poly(g,[(128,24),(227,19),(228,114),(127,117)],'plaster2')
 poly(g,[(225,21),(320,27),(320,116),(227,114)],'plaster0')
 for i in range(105):
  x=rng.randrange(129,319);y=rng.randrange(29,116)
  r(g,x,y,rng.randrange(1,4),1,rng.choice(['plaster1','plaster2','plaster0']))
 # Two recessed window bays, not a flat repeated texture.
 for x,w in [(143,32),(181,35)]:
  r(g,x-3,27,w+6,61,'brown');r(g,x,29,w,56,'metal0');r(g,x+2,31,w-4,51,'glass0')
  for col in range(3):
   for row in range(4):
    xx=x+3+col*9;yy=32+row*12;r(g,xx,yy,8,10,'glass1' if row<3 else 'glass0')
    if (row+col)%2==0:poly(g,[(xx,yy),(xx+4,yy),(xx+8,yy+6),(xx+8,yy+9)],'glass2')
  for yy in [42,54,66,78]:r(g,x+1,yy,w-2,2,'metal0');r(g,x+1,yy,w-2,1,'metal1')
  for xx in [x+11,x+20]:r(g,xx,29,2,55,'metal0');r(g,xx,29,1,55,'metal2')
  r(g,x-4,85,w+8,4,'plaster0');r(g,x-4,85,w+8,1,'cream')
  poly(g,[(x-3,89),(x+w+3,89),(x+w-1,91),(x,91)],'brown')
 # Ceiling trusses recede into the scene.
 for a,b in [((0,8),(320,9)),((0,28),(320,21)),((16,0),(53,38)),((125,0),(143,28)),((255,0),(235,26))]:
  line(g,a,b,2,'wood0');line(g,(a[0],a[1]-1),(b[0],b[1]-1),.6,'wood2')
 for x in [4,39,74,109,144,179,214,249,284]:r(g,x,8,1,2,'sand')
 r(g,125,22,7,97,'wood0');r(g,125,23,2,94,'wood2');r(g,130,23,1,94,'brown')
 # Rear corridor with perspective, shelves and depth.
 r(g,239,53,38,64,'wood0');poly(g,[(242,56),(274,57),(274,114),(242,115)],'deep')
 poly(g,[(242,56),(251,60),(251,110),(242,115)],'brown')
 r(g,253,63,17,41,'metal0');r(g,255,64,12,39,'glass0')
 for yy in [71,81,91]:r(g,253,yy,17,1,'metal2')
 r(g,236,51,43,4,'wood2');r(g,236,51,43,1,'sand')
 shelf(g,282,38,33,79)
 # Tool board and workbench along the left wall.
 r(g,43,48,74,47,'wood0');r(g,45,49,70,44,'wood1');r(g,45,49,70,1,'wood3')
 for x,y,length in [(51,58,19),(59,60,14),(68,56,23),(78,62,18),(88,57,20),(99,62,16),(108,55,22)]:
  line(g,(x,y),(x-1,y+length),.65,'steel2');ellipse(g,x,y,2,2,'steel1');r(g,x,y,1,2,'wood0')
  if x%2:line(g,(x-3,y+length),(x+2,y+length),.7,'steel1')
  else:r(g,x-2,y+length-2,4,4,'steel1');r(g,x-1,y+length-1,2,2,'wood1')
 plank(g,34,97,87,4);r(g,39,101,4,22,'wood1');r(g,109,101,5,18,'wood1')
 for x in [45,70,90]:r(g,x,103,21,13,'wood0');r(g,x+1,104,19,11,'wood2');r(g,x+8,108,5,2,'steel0')
 g.paste(crate(19,12),35,83);r(g,81,89,20,7,'metal1');r(g,83,89,16,1,'metal3')
 for x in [88,93,98]:r(g,x,85,1,7,'steel2')
 # Notice papers are small objects in the set, never large video title cards.
 r(g,219,70,16,23,'wood0');r(g,220,71,14,21,'wood2');r(g,222,73,10,12,'cream')
 for yy in [76,79,82]:r(g,224,yy,6,1,'plaster0')
 r(g,222,87,8,4,'clay')
 # Hoses and a hanging jacket add period workshop detail.
 for d in [0,3,6]:
  for a,b in zip([(21+d,56),(16+d,68),(17+d,83),(22+d,92),(29+d,89),(33+d,75),(30+d,59)],[(16+d,68),(17+d,83),(22+d,92),(29+d,89),(33+d,75),(30+d,59),(21+d,56)]):line(g,a,b,.7,'wood0')
 poly(g,[(225,44),(229,40),(234,42),(237,50),(235,62),(231,60),(229,64),(225,62),(224,52),(221,53),(220,48)],'blue0')
 line(g,(228,46),(229,61),.6,'blue2')
 # Foreground floor is built in perspective with broken stone and oily patches.
 poly(g,[(0,124),(134,113),(227,112),(320,119),(320,180),(0,180)],'floor1')
 poly(g,[(136,115),(183,113),(262,159),(127,161),(80,149)],'floor2')
 poly(g,[(179,115),(217,114),(320,149),(320,170),(259,158)],'floor3')
 for yy in [120,130,144,162,179]:
  line(g,(0,yy),(320,yy-3),.5,'floor0')
 for x in [-200,-88,20,123,245,375,528]:
  line(g,(188+(x-188)*.07,114),(x,179),.5,'floor0')
 for i in range(170):
  x=rng.randrange(320);y=rng.randrange(117,177)
  r(g,x,y,rng.choice([1,2,3,4]),1,rng.choice(['floor0','floor1','floor2','floor3']))
 # Distinct machines and storage occupy the edges, leaving an acting space.
 g.paste(barrel(),260,112);g.paste(crate(25,17),282,122);g.paste(crate(24,12),286,110)
 r(g,174,98,42,3,'wood0');r(g,174,97,42,1,'sand');r(g,178,101,3,16,'wood1');r(g,211,101,3,15,'wood1')
 r(g,187,88,18,9,'metal0');r(g,188,88,16,2,'metal3');r(g,201,82,2,7,'steel1');r(g,198,81,7,2,'steel2')
 # Small red oil can, folded rag and a wire basket.
 r(g,207,91,5,6,'red1');r(g,209,89,1,3,'red2');line(g,(211,91),(215,89),.5,'steel1')
 poly(g,[(70,95),(73,89),(79,91),(82,96)],'plaster3');r(g,76,92,2,4,'plaster1')
 for x in range(145,166,3):r(g,x,99,1,14,'steel0')
 r(g,144,100,23,1,'steel1');r(g,144,111,23,2,'steel0')
 # Warm lamps. All light marks retain hard logical-pixel edges.
 for x,y in [(75,32),(193,21)]:
  r(g,x,9,1,y-9,'black');poly(g,[(x-3,y),(x+3,y),(x+10,y+5),(x-10,y+5)],'metal0')
  r(g,x-8,y+5,16,2,'gold');r(g,x-3,y+6,6,1,'ivory')
 return g

def lathe():
 g=Geometry()
 # A compact 1960s lathe: bed, chuck, carriage, lead screw and two supports.
 poly(g,[(0,18),(83,18),(89,22),(85,25),(0,25)],'metal0')
 r(g,1,18,83,2,'metal4');r(g,2,21,81,1,'metal2')
 for x in [7,70]:
  poly(g,[(x,24),(x+12,24),(x+14,45),(x-1,45)],'metal0');r(g,x+2,25,8,16,'metal1');r(g,x+2,25,2,15,'metal2')
  r(g,x-3,44,20,3,'metal0');r(g,x-2,44,18,1,'steel1')
 r(g,5,5,24,14,'metal0');poly(g,[(5,5),(10,1),(28,1),(33,6),(30,18),(5,18)],'metal1')
 r(g,10,2,18,2,'metal3');r(g,7,6,3,10,'metal2');r(g,11,7,10,6,'metal0')
 for x in [13,17]:r(g,x,9,2,2,'red1' if x==13 else 'green')
 r(g,28,7,7,9,'steel0');r(g,30,7,2,9,'steel3');r(g,33,8,2,7,'steel1')
 r(g,34,10,43,4,'steel1');r(g,35,10,42,1,'steel3');r(g,36,13,39,1,'metal0')
 poly(g,[(71,5),(77,5),(82,9),(82,18),(68,18),(68,12)],'metal1');r(g,73,6,4,2,'metal3')
 r(g,75,18,11,3,'metal2');r(g,80,12,8,2,'steel1')
 r(g,40,15,19,9,'metal1');r(g,42,14,14,2,'metal3');r(g,50,9,4,7,'metal0');r(g,48,8,8,2,'steel2')
 r(g,45,23,8,8,'metal0');r(g,46,24,6,2,'metal3');g.paste(cog(4),50,28)
 r(g,18,27,54,1,'steel1')
 for x in range(20,70,3):r(g,x,27,1,1,'steel3')
 for x,y in [(7,7),(24,6),(6,16),(28,17),(41,19),(56,19),(79,17)]:r(g,x,y,1,1,'sand')
 return g

def foreground():
 g=Geometry()
 # Large cropped objects give the room a near plane.
 g.paste(crate(33,25),-6,142);g.paste(crate(19,13),2,130)
 g.paste(barrel(18,24),26,145)
 for x,y,radius in [(51,161,10),(66,160,7),(39,153,6)]:g.paste(cog(radius),x,y)
 r(g,0,0,5,158,'wood0');r(g,3,0,2,140,'brown')
 r(g,312,0,8,169,'metal0');r(g,313,0,2,169,'metal2');r(g,315,0,1,169,'steel1')
 for y in range(7,169,17):r(g,314,y,1,2,'steel3')
 g.paste(barrel(20,32,'red0'),291,142)
 r(g,296,146,4,22,'red1');r(g,300,148,2,14,'red2')
 for i in range(3):
  ellipse(g,276+i*5,158-i,13,7,'metal0');ellipse(g,276+i*5,158-i,10,5,'steel0');ellipse(g,276+i*5,158-i,7,3,'black')
 return g

def worker(kind='lula',pose='idle',phase=0,flip=False,gesture=.5):
 """Approximately 20 × 51 logical pixels. No enlarged portrait or source image."""
 g=Geometry();walk=pose=='walk';s=math.sin(phase);bob=round(.6*(1-math.cos(phase*2))) if walk else 0
 shirt=['blue0','blue1','blue2'] if kind=='lula' else ['wood1','ochre','sand']
 if kind=='back':shirt=['metal0','metal1','metal2']
 shift=-1 if pose=='work' else 0
 def pt(x,y):return(x+shift,y+bob)
 # Far leg and near leg have two-cycle foot contact rather than a global sway.
 for i in [0,1]:
  hip=(10+i*5,30+bob)
  if walk:
   u=(phase/(2*math.pi)+i*.5)%1
   if u<.5:dx=15*(.25-u);lift=0
   else:
    z=(u-.5)*2;dx=15*(-.25+.5*z*z*(3-2*z));lift=4*math.sin(z*math.pi)
   f=(9+i*7+dx,49-lift)
   knee=((hip[0]+f[0])*.5+2,40-lift*.5)
  else:f=(9+i*7,49);knee=(10+i*6,40)
  line(g,hip,knee,2.2,'trouser0');line(g,knee,(f[0],f[1]-2),1.7,'trouser0')
  line(g,(hip[0]-1,hip[1]+2),(knee[0]-1,knee[1]),.6,'trouser2' if i else 'trouser1')
  line(g,(knee[0],knee[1]+1),(f[0]-1,f[1]-2),.6,'trouser1')
  poly(g,[(f[0]-2,f[1]-2),(f[0]+2,f[1]-2),(f[0]+4,f[1]),(f[0]+4,f[1]+1),(f[0]-2,f[1]+1)],'black')
  r(g,f[0]-1,f[1]-1,3,1,'steel0')
 # Far arm is behind a continuous torso.
 far=(6-3*s,33) if walk else (6,33)
 if pose=='work':far=(3,27)
 line(g,pt(7,17),pt(5,24),2,shirt[0]);line(g,pt(5,24),pt(*far),1.2,'skin0');r(g,far[0]-1+shift,far[1]+bob,2,3,'skin1')
 poly(g,[pt(8,14),pt(14,13),pt(18,16),pt(19,23),pt(17,31),pt(8,31),pt(6,25),pt(6,18)],shirt[1])
 poly(g,[pt(8,16),pt(10,15),pt(10,25),pt(12,28),pt(9,29),pt(7,25)],shirt[2])
 poly(g,[pt(16,16),pt(18,18),pt(18,26),pt(17,30),pt(14,29),pt(15,25)],shirt[0])
 line(g,pt(13,18),pt(13,29),.5,shirt[0]);r(g,14+shift,22+bob,3,3,shirt[0]);r(g,14+shift,22+bob,3,1,shirt[2])
 r(g,8+shift,30+bob,9,1,'wood0');r(g,13+shift,30+bob,2,1,'cream')
 # Face: nine pixels high, eyes and moustache are single marks.
 r(g,11+shift,10+bob,4,5,'skin0')
 poly(g,[pt(10,4),pt(13,2),pt(17,4),pt(17,8),pt(19,9),pt(17,10),pt(16,13),pt(12,13),pt(10,10)],'skin1')
 poly(g,[pt(14,5),pt(17,5),pt(17,8),pt(18,9),pt(16,10),pt(16,12),pt(14,12),pt(13,9)],'skin2')
 r(g,16+shift,7+bob,1,1,'ink')
 poly(g,[pt(9,5),pt(10,2),pt(13,1),pt(17,3),pt(18,5),pt(15,4),pt(13,5),pt(11,7),pt(11,10),pt(9,9)],'hair')
 r(g,11+shift,3+bob,4,1,'brown')
 if kind=='chico':r(g,15+shift,10+bob,3,1,'hair')
 elif pose!='work':r(g,16+shift,10+bob,2,1,'brown')
 poly(g,[pt(10,14),pt(12,13),pt(13,16),pt(12,18)],shirt[2]);poly(g,[pt(14,13),pt(17,15),pt(15,18),pt(13,16)],shirt[2])
 # Small explicit arm poses, built from coherent limb segments.
 shoulder=pt(17,17)
 if walk:elbow=pt(18,25);wrist=pt(18+3*s,33)
 elif pose=='work':elbow=pt(16,24);wrist=pt(7+round(math.sin(phase)),27)
 elif pose=='talk':elbow=pt(18,26);wrist=pt(22+3*gesture,25-6*gesture)
 else:elbow=pt(18,25);wrist=pt(18,33)
 line(g,shoulder,elbow,2,shirt[1]);line(g,pt(17,18),pt(17,22),.7,shirt[2])
 line(g,elbow,wrist,1.2,'skin1');line(g,(elbow[0]-1,elbow[1]),(wrist[0]-1,wrist[1]),.5,'skin2')
 r(g,wrist[0]-1,wrist[1],3,2,'skin2')
 if pose=='talk':r(g,wrist[0]+1,wrist[1]-1,2,1,'skin1')
 # A selective dark edge underneath the figure; no thick universal outline.
 if flip:
  q=Geometry()
  for (x,y),c in g.cells.items():q.cells[27-x,y]=c
  return q
 return g
