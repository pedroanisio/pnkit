"""Original procedural sets for the 1978–2021 chapter, at 320 x 180."""
from .geometry import Geometry
from .scene_art import P,r,poly,line,ellipse,lettering,plank,crate,barrel,shelf,lathe
from .story_art import actor as base_actor,flip,resize,tree,chair,table,hall,prison,podium
import math,random

def label(g,txt,x,y,c='cream'):
 q,_=lettering(txt,c);g.paste(q,x,y);return g

def actor(kind='lula78',pose='idle',phase=0,facing=False,gesture=.5):
 if pose=='sit' and kind.startswith('lula'):
  g=actor(kind,'idle',phase,False,gesture);g.cells={xy:c for xy,c in g.cells.items() if xy[1]<31}
  for i in [0,1]:
   line(g,(9+i*6,30),(17+i*6,33),2,'trouser0');line(g,(17+i*6,33),(18+i*6,42),1.7,'trouser0')
   line(g,(9+i*6,29),(17+i*6,32),.6,'trouser2');r(g,16+i*6,42,6,2,'black')
  return flip(g,27) if facing else g
 if kind.startswith('lula'):
  # Constant head size; silhouette and grouped beard pixels identify each age.
  g=base_actor('lula',pose,phase,False,gesture)
  era=kind[4:];suit=era in ['02','06','18','21'];bob=round(.6*(1-math.cos(phase*2))) if pose=='walk' else 0
  shirt={'blue0':'plaster1','blue1':'plaster3','blue2':'ivory'} if not suit else {'blue0':'black','blue1':'blue0','blue2':'blue1'}
  g.cells={xy:{P[a]:P[b] for a,b in shirt.items()}.get(c,c) for xy,c in g.cells.items()}
  if suit:
   poly(g,[(10,14+bob),(14,13+bob),(17,15+bob),(13,23+bob)],'ivory')
   poly(g,[(13,16+bob),(15,16+bob),(15,22+bob),(13,25+bob),(12,21+bob)],'red0')
  dark='hair' if era in ['78','89'] else ('steel0' if era in ['02','06'] else 'steel1')
  mid='brown' if era in ['78','89'] else ('steel1' if era in ['02','06'] else 'steel2')
  light='wood1' if era in ['78','89'] else ('steel2' if era in ['02','06'] else 'steel3')
  if era in ['18','21']:
   for (x,y),c in list(g.cells.items()):
    if y<=10+bob and c==P['hair']:g.cells[x,y]=P['steel2']
    if y<=5+bob and c==P['brown']:g.cells[x,y]=P['steel3']
  elif era in ['02','06']:
   r(g,10,5+bob,2,5,'steel1');r(g,11,3+bob,3,1,'steel1')
  poly(g,[(10,8+bob),(12,10+bob),(14,10+bob),(16,9+bob),(18,10+bob),(18,14+bob),(15,17+bob),(11,15+bob),(10,12+bob)],dark)
  poly(g,[(11,11+bob),(13,13+bob),(16,13+bob),(17,11+bob),(17,14+bob),(14,16+bob),(12,14+bob)],mid)
  r(g,14,14+bob,2,1,light);r(g,15,11+bob,3,1,'skin0');r(g,16,7+bob,1,1,'black')
  if era=='89':r(g,11,13+bob,1,2,'steel1')
  return flip(g,27) if facing else g
 if kind=='alencar':
  g=base_actor('clerk',pose,phase,False,gesture);bob=round(.6*(1-math.cos(phase*2))) if pose=='walk' else 0
  colors={P['wood0']:P['blue0'],P['brown']:P['steel1'],P['clay']:P['blue2'],P['hair']:P['steel2']}
  g.cells={xy:colors.get(c,c) for xy,c in g.cells.items()}
  poly(g,[(10,14+bob),(15,14+bob),(13,22+bob)],'ivory');r(g,13,17+bob,1,6,'red0')
  return flip(g,27) if facing else g
 if kind=='dilma':
  g=base_actor('mother',pose,phase,False,gesture)
  # Red jacket, trousers, short rounded hair; distinct from Dona Lindu.
  g.cells={xy:c for xy,c in g.cells.items() if xy[1]<14 or xy[1]>=44}
  poly(g,[(8,14),(15,14),(19,18),(19,31),(6,31),(6,20)],'red1');r(g,7,17,2,11,'red2');r(g,16,17,3,12,'red0')
  poly(g,[(9,14),(14,14),(13,20)],'ivory');r(g,12,21,1,8,'gold')
  for x in [9,15]:line(g,(x,31),(x-1,47),1.7,'trouser0');r(g,x-3,47,6,2,'black')
  line(g,(7,18),(5,26),1.8,'red1');line(g,(5,26),(6,33),1,'skin1')
  w=(24,24-gesture*3) if pose=='talk' else (19,33)
  line(g,(17,18),(19,25),1.8,'red1');line(g,(19,25),w,1,'skin1');r(g,w[0]-1,w[1],3,2,'skin2')
  poly(g,[(7,4),(8,1),(12,0),(16,2),(18,5),(15,4),(12,5),(10,8),(10,12),(7,11)],'brown');r(g,9,2,5,1,'clay')
  return flip(g,27) if facing else g
 return base_actor(kind,pose,phase,facing,gesture)

def crowd(width=320,rows=5,seed=70,back=False):
 g=Geometry();rng=random.Random(seed)
 for row in range(rows):
  y=row*8;size=2+row//2
  for x in range(-5+(row%2)*6,width+9,11+row):
   yy=y+rng.randrange(-1,2);shirt=rng.choice(['blue0','metal1','wood1','plaster3','red0','steel0'])
   poly(g,[(x-size-2,yy+6),(x-2,yy+3),(x+size,yy+3),(x+size+3,yy+8),(x+size+3,yy+15),(x-size-2,yy+15)],shirt)
   ellipse(g,x,yy,2.5,3.5,'hair' if back else rng.choice(['skin0','skin1','skin2']))
   r(g,x-2,yy-3,4,2,'hair')
   if not back:r(g,x+1,yy,1,1,'ink')
 return g

def flag(phase=0,color='red1',text=None):
 g=Geometry();line(g,(0,0),(0,36),.6,'wood1');poly(g,[(1,1),(12,3+round(2*math.sin(phase))),(26,1),(24,17),(13,19+round(math.sin(phase))),(1,16)],color)
 if text:label(g,text,6,7,'ivory')
 return g

def gate():
 g=Geometry();rng=random.Random(1978);r(g,0,0,320,180,'glass0')
 for x,y,w in [(37,20,46),(164,31,49),(284,14,51)]:ellipse(g,x,y,w,3,'glass1')
 for x,y,h in [(60,24,68),(203,16,76),(267,39,55)]:r(g,x,y,7,h,'brick');r(g,x,y,2,h,'clay');r(g,x-2,y,11,3,'wood0')
 poly(g,[(0,58),(38,42),(38,57),(78,39),(78,58),(120,39),(120,95),(0,108)],'plaster0')
 poly(g,[(200,66),(233,51),(233,64),(275,44),(275,66),(320,49),(320,108),(200,108)],'steel0')
 for x in range(8,312,24):r(g,x,73,16,20,'metal0');r(g,x+1,74,13,1,'steel1')
 r(g,0,111,320,69,'floor1');poly(g,[(120,102),(220,102),(279,160),(74,160)],'steel0')
 for i in range(150):r(g,rng.randrange(320),rng.randrange(113,160),rng.choice([1,2,4]),1,rng.choice(['floor0','floor2','steel1']))
 for x,w in [(0,111),(236,84)]:
  r(g,x,81,w,37,'brick')
  for yy in range(82,118,5):
   for xx in range(x-9+(yy//5%2)*8,x+w,17):r(g,xx,yy,15,1,'clay')
  r(g,x-1,78,w+2,4,'plaster0');r(g,x-1,78,w+2,1,'plaster2')
 for x in [107,227]:r(g,x,53,9,68,'wood0');r(g,x,53,2,67,'steel1');r(g,x-2,51,13,3,'steel0')
 for x in range(119,225,7):r(g,x,64,1,52,'metal0')
 r(g,115,62,113,2,'steel1');r(g,115,96,113,2,'steel1')
 r(g,102,45,139,10,'blue0');label(g,'METALÚRGICA',139,47,'steel3')
 g.paste(barrel(19,27),20,127);g.paste(crate(25,17),275,132)
 tree(g,311,119,61,3)
 return g

def stadium():
 g=Geometry();r(g,0,0,320,180,'glass1');r(g,0,42,320,19,'glass2')
 for x,y,w in [(44,23,33),(193,31,45)]:ellipse(g,x,y,w,3,'ivory')
 poly(g,[(0,64),(61,43),(94,58),(150,48),(200,61),(273,43),(320,61),(320,88),(0,88)],'metal2')
 for yy in [74,83,92,103]:r(g,0,yy,320,2,'plaster1');r(g,0,yy+2,320,1,'plaster3')
 for x in [21,297]:r(g,x,16,2,83,'steel0');r(g,x-9,14,20,3,'steel1')
 g.paste(crowd(320,5,1979),0,73)
 r(g,0,119,320,61,'floor1');r(g,55,135,190,9,'wood0');r(g,57,130,186,6,'wood2');r(g,57,130,186,1,'sand')
 for x in [57,240]:r(g,x,117,3,19,'wood0')
 line(g,(56,119),(242,119),.5,'steel1')
 return g

def union_door():
 g=hall();r(g,90,28,140,87,'plaster2');r(g,105,40,110,77,'wood0');r(g,109,44,102,72,'wood1')
 for x in range(112,210,10):r(g,x,45,1,70,'wood3')
 r(g,159,43,3,75,'black');r(g,151,76,2,8,'steel2');r(g,169,76,2,8,'steel2')
 r(g,114,51,92,27,'plaster3');label(g,'INTERVENÇÃO',129,56,'wood0');label(g,'1980',147,67,'wood0')
 return g

def detention(modern=False):
 g=Geometry();rng=random.Random(80);r(g,0,0,320,180,'plaster1')
 poly(g,[(0,0),(52,25),(52,119),(0,152)],'plaster0');poly(g,[(52,25),(320,13),(320,114),(52,119)],'plaster2')
 if not modern:
  for yy in range(26,117,15):line(g,(52,yy),(320,yy-7),.5,'plaster0')
  for x in range(77,319,43):line(g,(x,24),(x,116),.5,'plaster1')
 r(g,0,120,320,60,'floor1')
 for y in [128,143,160]:r(g,0,y,320,1,'floor0')
 for x in [40,112,196,286]:line(g,(130+(x-130)*.2,120),(x,180),.5,'floor0')
 r(g,67,36,58,44,'steel0');r(g,71,40,50,35,'glass0')
 for x in range(76,120,9):r(g,x,40,2,35,'steel1')
 r(g,71,57,50,2,'steel0');r(g,65,80,63,3,'plaster3')
 poly(g,[(72,83),(121,83),(211,141),(112,141)],'floor2')
 r(g,228,109,77,10,'wood0');r(g,232,104,69,8,'plaster3');r(g,232,103,69,2,'ivory')
 r(g,234,100,18,5,'cream');r(g,258,104,42,5,'blue1')
 for x in [229,301]:r(g,x,118,3,24,'steel0')
 g.paste(table(),133,111);g.paste(chair(),169,103)
 if modern:
  r(g,263,29,39,51,'wood0');r(g,265,31,35,47,'wood2')
  for y in [47,62,77]:r(g,264,y,37,2,'sand')
  for x in range(268,297,5):r(g,x,34,3,12,'blue0' if x%2 else 'red0');r(g,x,51,3,9,'plaster3')
  r(g,137,107,21,2,'cream');r(g,141,104,16,3,'ivory')
 else:
  r(g,282,81,14,13,'wood0');r(g,283,82,12,11,'cream');label(g,'31',284,84,'wood0')
 return g

def bars():
 g=Geometry()
 for x in range(4,320,31):r(g,x,0,4,160,'metal0');r(g,x+1,0,1,160,'steel1')
 r(g,0,31,320,4,'metal0');r(g,0,132,320,4,'metal0')
 return g

def pt_room():
 g=hall();r(g,112,29,105,63,'plaster2');r(g,122,32,83,38,'red0');label(g,'PT',158,42,'ivory');label(g,'1980',150,56,'cream')
 r(g,130,78,67,19,'cream');label(g,'FUNDAÇÃO',141,83,'wood0')
 return g

def plaza():
 g=Geometry();r(g,0,0,320,180,'glass1');r(g,0,52,320,44,'glass2')
 for x,w,h in [(0,45,68),(49,41,93),(93,36,57),(251,38,77),(292,31,88)]:
  r(g,x,113-h,w,h,'plaster1');r(g,x+2,115-h,w-4,h-2,'plaster2')
  for xx in range(x+6,x+w-4,11):
   for yy in range(122-h,99,13):r(g,xx,yy,5,7,'glass0')
 tree(g,221,110,76,4);r(g,0,113,320,67,'floor1')
 g.paste(crowd(320,4,1984),0,111)
 r(g,91,96,136,11,'wood0');r(g,91,95,136,1,'sand')
 r(g,105,65,108,20,'gold');label(g,'DIRETAS JÁ',127,72,'wood0')
 return g

def congress(exterior=False):
 g=Geometry();r(g,0,0,320,180,'blue2')
 if exterior:
  r(g,0,98,320,82,'metal2');r(g,0,140,320,40,'steel1');r(g,111,24,25,81,'plaster3');r(g,143,24,25,81,'plaster3')
  for x in [114,120,126,132,146,152,158,164]:r(g,x,27,1,74,'steel1')
  r(g,40,102,235,9,'ivory');r(g,45,111,225,6,'plaster1')
  ellipse(g,77,100,30,12,'ivory');r(g,47,101,61,12,'blue2')
  ellipse(g,228,97,31,13,'ivory');r(g,196,83,65,13,'blue2')
  r(g,0,127,320,7,'glass0');r(g,4,128,312,1,'glass2')
 else:
  r(g,0,0,320,180,'wood0');poly(g,[(0,0),(320,0),(282,99),(38,99)],'wood1')
  for x in range(0,320,9):line(g,(x,10),(120+(x-120)*.7,93),.6,'wood2')
  r(g,93,29,133,41,'black');label(g,'SENADO',140,37,'cream')
  r(g,25,93,270,14,'wood2');r(g,25,93,270,2,'sand');r(g,0,109,320,71,'floor0')
  for row in range(4):
   yy=117+row*12
   for x in range(14-row*3,309,32):
    poly(g,[(x,yy),(x+25,yy),(x+28,yy+5),(x-2,yy+5)],'wood2');r(g,x-2,yy+5,30,3,'wood0')
    ellipse(g,x+12,yy-6,3,4,'hair');r(g,x+8,yy-2,9,4,'blue0')
 return g

def television():
 g=Geometry();r(g,0,0,320,180,'plaster1');r(g,0,104,320,76,'floor1')
 for y in [118,140,162]:r(g,0,y,320,1,'floor0')
 shelf(g,258,29,50,78);r(g,9,25,57,64,'wood1');r(g,13,29,49,56,'glass0')
 r(g,36,28,3,60,'wood2');r(g,12,56,51,2,'wood2');r(g,6,89,64,3,'cream')
 g.paste(table(),116,122)
 r(g,91,37,155,87,'wood0');r(g,94,40,149,81,'wood2');r(g,99,43,117,73,'black')
 r(g,103,47,109,65,'blue0');r(g,106,49,102,1,'blue2')
 for y in [55,76]:ellipse(g,230,y,6,6,'black');ellipse(g,230,y,4,4,'steel0');line(g,(230,y),(232,y-3),.6,'steel2')
 for y in range(88,113,4):r(g,222,y,15,1,'wood0')
 line(g,(161,37),(133,14),.7,'steel0');line(g,(161,37),(192,17),.7,'steel0')
 g.paste(barrel(21,30),22,132);r(g,25,127,15,7,'metal0')
 for x in [26,32,38]:line(g,(32,129),(x-4,110),.8,'green')
 return g

def campaign():
 g=hall();r(g,88,28,146,64,'plaster2');r(g,101,35,119,39,'red0')
 label(g,'LULA',145,43,'ivory');label(g,'2002',143,58,'cream')
 g.paste(table(),21,119);g.paste(crate(28,22),268,117)
 for x,y in [(21,118),(29,116),(40,117)]:r(g,x,y,14,3,'cream')
 return g

def planalto():
 g=Geometry();r(g,0,0,320,180,'blue2');r(g,0,62,320,26,'glass2');r(g,0,111,320,69,'metal2')
 r(g,35,43,270,13,'ivory');r(g,40,58,260,45,'glass0');r(g,40,58,260,2,'glass2')
 for x in range(42,302,10):r(g,x,60,1,42,'steel1')
 for x in [47,116,185,254]:
  poly(g,[(x,43),(x+11,43),(x+6,65),(x+5,83),(x+17,104),(x+8,104),(x-1,86),(x-1,65)],'ivory')
 r(g,31,104,278,6,'plaster3');r(g,31,104,278,1,'ivory')
 poly(g,[(146,107),(184,107),(241,156),(187,156)],'plaster3');line(g,(146,107),(187,156),1,'ivory');line(g,(184,107),(241,156),1,'ivory')
 line(g,(146,96),(187,145),.5,'steel0');line(g,(184,96),(241,145),.5,'steel0')
 for x,y in [(149,110),(165,129),(187,156),(188,110),(215,133),(240,155)]:r(g,x,y-10,1,10,'steel0')
 r(g,0,158,320,22,'steel1');r(g,9,122,111,12,'glass0');r(g,12,124,104,1,'glass2')
 for x in [10,283,310]:tree(g,x,131,47,12+x)
 return g

def office():
 g=Geometry();r(g,0,0,320,180,'plaster2');r(g,0,116,320,64,'floor1')
 for yy in [124,139,157]:r(g,0,yy,320,1,'floor0')
 r(g,89,26,144,74,'wood0');r(g,93,30,136,66,'glass1')
 # Brasilia skyline, framed by the presidential office window.
 r(g,94,73,134,23,'green');r(g,147,44,9,38,'plaster3');r(g,162,44,9,38,'plaster3');r(g,112,79,99,4,'ivory')
 ellipse(g,126,79,12,5,'ivory');ellipse(g,195,77,12,5,'ivory');r(g,183,71,24,5,'glass1')
 r(g,158,29,3,68,'wood1');r(g,92,98,139,3,'cream')
 shelf(g,255,27,53,89)
 line(g,(41,31),(41,129),1,'wood2');poly(g,[(42,32),(76,36),(73,79),(42,75)],'green');poly(g,[(46,53),(58,42),(70,56),(58,69)],'gold');ellipse(g,58,55,6,6,'blue0')
 r(g,111,106,109,8,'wood0');poly(g,[(116,98),(211,98),(221,106),(109,106)],'wood2');r(g,111,105,109,1,'sand')
 for x in [116,205]:r(g,x,114,8,28,'wood1');r(g,x,114,1,28,'wood3')
 r(g,118,117,38,21,'wood1');r(g,122,120,30,1,'wood3');r(g,134,125,6,2,'wood0')
 poly(g,[(146,100),(169,100),(173,104),(149,104)],'ivory');r(g,151,101,14,1,'plaster1')
 r(g,189,97,11,7,'black');r(g,188,96,13,3,'steel0')
 g.paste(chair(),170,88)
 return g

def classroom():
 g=hall();r(g,82,29,153,68,'plaster2');r(g,89,35,139,52,'wood1');r(g,92,38,133,45,'metal0')
 label(g,'ESCOLA',137,43,'ivory');label(g,'A B C',125,59,'cream');label(g,'1 2 3',164,70,'cream')
 r(g,86,87,147,3,'wood2')
 for row in range(2):
  for x in [39,89,139,189]:
   xx=x+row*12;yy=120+row*23
   r(g,xx,yy,31,3,'wood2');r(g,xx,yy,31,1,'sand');r(g,xx+2,yy+3,2,13,'wood0');r(g,xx+26,yy+3,2,13,'wood0')
   ellipse(g,xx+13,yy-11,4,5,'hair');r(g,xx+8,yy-5,11,8,'blue1' if x%3 else 'plaster3')
 return g

def market():
 g=Geometry();r(g,0,0,320,180,'plaster1');r(g,0,115,320,65,'floor1')
 shelf(g,12,28,76,79);shelf(g,219,28,87,79)
 r(g,101,32,103,25,'metal0');label(g,'MERCEARIA',126,40,'cream')
 r(g,101,65,27,40,'wood0');r(g,103,67,23,35,'glass0');r(g,108,71,12,16,'plaster3')
 for x in [126,151,177]:g.paste(crate(24,14),x,107)
 rng=random.Random(42)
 for x in range(127,199,5):
  for y in [104,109]:ellipse(g,x,y,2,2,rng.choice(['red1','gold','green']))
 r(g,82,126,140,5,'wood2');r(g,82,126,140,1,'sand');r(g,86,131,132,26,'wood1')
 for x in [89,128,169,208]:r(g,x,134,1,20,'wood3')
 r(g,189,113,22,12,'steel0');r(g,191,114,18,5,'glass0');r(g,191,120,18,1,'steel2')
 g.paste(barrel(21,28),18,133);g.paste(crate(29,17),277,137)
 return g

def home():
 g=television();r(g,89,35,158,91,'plaster1');g.paste(table(),98,123)
 r(g,118,121,31,3,'cream');ellipse(g,134,121,10,2,'ivory');ellipse(g,167,121,9,2,'cream')
 r(g,207,79,47,38,'wood0');r(g,210,82,33,29,'blue0');r(g,246,84,4,4,'steel1');r(g,246,99,4,10,'wood2')
 for x in [211,246]:r(g,x,117,3,18,'wood1')
 r(g,198,137,62,4,'wood2');r(g,201,141,4,18,'wood1');r(g,252,141,4,18,'wood1')
 return g

def stf():
 g=Geometry();r(g,0,0,320,180,'blue2');r(g,0,99,320,81,'steel1')
 r(g,40,47,256,9,'ivory');r(g,52,59,236,44,'glass0');r(g,49,104,240,6,'plaster3')
 for x in range(58,285,11):r(g,x,60,1,42,'steel1')
 for x in [54,97,140,183,226,269]:poly(g,[(x,52),(x+7,52),(x+4,91),(x+12,103),(x+4,103),(x-2,92)],'ivory')
 r(g,30,111,274,3,'plaster2');r(g,23,115,285,3,'plaster3');r(g,17,119,297,3,'plaster2')
 # Seated Justice silhouette with sword in front of the building.
 r(g,66,132,36,8,'plaster0');r(g,72,119,25,14,'plaster2');ellipse(g,83,102,5,6,'plaster3')
 poly(g,[(78,108),(88,108),(92,120),(96,125),(76,126),(78,117)],'plaster3');line(g,(78,121),(73,132),2,'plaster3');line(g,(86,121),(92,132),2,'plaster3')
 line(g,(88,114),(102,114),1,'plaster2');line(g,(101,110),(101,138),.6,'steel0')
 for y in [141,157]:r(g,0,y,320,1,'steel0')
 for x in [10,99,213,306]:line(g,(160+(x-160)*.2,123),(x,180),.6,'steel0')
 return g

def papers():
 g=Geometry();r(g,0,0,320,180,'wood0')
 for y in range(0,180,12):plank(g,0,y,320,12)
 poly(g,[(56,34),(240,34),(254,149),(61,152)],'brown')
 poly(g,[(50,27),(237,27),(247,144),(53,146)],'plaster3')
 poly(g,[(56,23),(243,23),(248,141),(59,143)],'ivory')
 label(g,'SUPREMO TRIBUNAL FEDERAL',80,36,'wood0');label(g,'HC 193726',133,50,'wood1')
 for y,w in [(65,131),(70,139),(75,117),(103,120),(108,134),(113,111)]:r(g,78,y,w,1,'plaster1')
 label(g,'2021',133,122,'wood1')
 line(g,(271,55),(279,132),1.2,'blue0');line(g,(271,55),(272,69),.5,'steel2')
 ellipse(g,26,56,13,10,'black');ellipse(g,26,54,12,8,'steel1');ellipse(g,26,54,9,6,'wood0')
 return g
