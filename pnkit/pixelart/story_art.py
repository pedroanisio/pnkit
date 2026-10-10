"""Story sets and small actors on the approved 320 x 180 logical grid."""
from .geometry import Geometry
from .scene_art import P,r,poly,line,ellipse,plank,crate,barrel,worker,lettering,shelf
import random, math

def resize(q,s):
 g=Geometry()
 for (x,y),c in q.cells.items():g.rect(x*s,y*s,s,s,c)
 return g

def flip(q,width=28):
 g=Geometry();g.cells={(width-x,y):c for (x,y),c in q.cells.items()};return g

def label(g,txt,x,y,c='cream'):
 q,_=lettering(txt,c);g.paste(q,x,y);return g

def actor(kind='lula',pose='idle',phase=0,facing=False,gesture=.5):
 if pose=='sit':
  g=actor(kind,'idle',phase,False,gesture);g.cells={xy:c for xy,c in g.cells.items() if xy[1]<31}
  for i in [0,1]:
   hip=(9+i*6,30);knee=(17+i*6,33);foot=(18+i*6,42)
   line(g,hip,knee,2,'trouser0');line(g,knee,foot,1.7,'trouser0')
   line(g,(hip[0],hip[1]-1),(knee[0],knee[1]-1),.6,'trouser1')
   line(g,(knee[0],knee[1]+1),(foot[0]-1,foot[1]-1),.5,'trouser2')
   r(g,foot[0]-2,foot[1],6,2,'black');r(g,foot[0]-1,foot[1],3,1,'steel0')
  return flip(g,27) if facing else g
 if kind in ['lula','chico','back']:return worker(kind,pose,phase,facing,gesture)
 if kind in ['old','leader','clerk']:
  g=worker('chico' if kind=='leader' else 'lula',pose,phase,False,gesture)
  remap={'old':{'blue0':'blue0','blue1':'blue1','blue2':'blue2','hair':'steel2','brown':'steel1'},
         'leader':{'wood1':'plaster1','ochre':'plaster3','sand':'ivory'},
         'clerk':{'blue0':'wood0','blue1':'brown','blue2':'clay'}}[kind]
  g.cells={xy:P[remap[k]] if (k:=next((k for k,v in P.items() if v==c and k in remap),None)) else c for xy,c in g.cells.items()}
  bob=round(.6*(1-math.cos(phase*2))) if pose=='walk' else 0
  if kind=='old':
   poly(g,[(10,9+bob),(13,11+bob),(17,10+bob),(17,13+bob),(14,15+bob),(11,13+bob)],'steel2')
   r(g,13,12+bob,3,2,'steel3');r(g,16,10+bob,2,1,'skin0')
  return flip(g,27) if facing else g
 if kind in ['child','sister']:
  g=worker('lula','walk' if pose=='walk' else 'idle',phase,False,gesture)
  remap={P['blue0']:P['wood1'],P['blue1']:P['ochre'],P['blue2']:P['sand']}
  g.cells={xy:remap.get(c,c) for xy,c in g.cells.items()}
  # Bare lower legs, shorts, child-sized head/body and short hair.
  for (x,y),c in list(g.cells.items()):
   if 38<y<47 and c in [P['trouser0'],P['trouser1'],P['trouser2']]:g.cells[x,y]=P['skin0'] if x%2 else P['skin1']
  g=resize(g,.65)
  if kind=='sister':
   poly(g,[(5,15),(11,15),(13,25),(4,25)],'red0');line(g,(4,25),(12,25),.5,'red2')
   r(g,6,2,2,7,'hair')
  return flip(g,18) if facing else g
 if kind=='mother':
  g=Geometry();walk=pose=='walk';s=math.sin(phase);bob=round(.5*(1-math.cos(2*phase))) if walk else 0
  for i in [0,1]:
   x=9+i*6+(3*s*(-1 if i else 1) if walk else 0);lift=max(0,math.cos(phase+i*math.pi))*2 if walk else 0
   line(g,(10+i*5,38+bob),(x,47-lift),1.2,'skin0');r(g,x-2,47-lift,6,2,'wood0')
  poly(g,[(9,14+bob),(15,14+bob),(18,21+bob),(18,31+bob),(22,44),(4,44),(7,30+bob),(7,21+bob)],'metal1')
  poly(g,[(9,16+bob),(12,17+bob),(10,31+bob),(8,41),(6,42),(8,29+bob)],'metal2')
  poly(g,[(16,18+bob),(18,22+bob),(17,31+bob),(20,43),(16,42),(14,30+bob)],'metal0')
  poly(g,[(9,27+bob),(15,27+bob),(18,40),(8,40)],'plaster3');r(g,8,27+bob,9,1,'cream')
  line(g,(13,29+bob),(14,38),.5,'plaster1')
  line(g,(7,18+bob),(5,26+bob),1.8,'metal1');line(g,(5,26+bob),(6-2*s if walk else 6,34+bob),1.1,'skin0')
  line(g,(17,18+bob),(19,25+bob),1.8,'metal1')
  wrist=(20+2*s,34) if walk else ((24,29) if pose=='talk' else (19,34))
  line(g,(19,25+bob),(wrist[0],wrist[1]+bob),1.1,'skin1');r(g,wrist[0]-1,wrist[1]+bob,3,2,'skin2')
  r(g,11,11+bob,4,5,'skin0')
  poly(g,[(9,4+bob),(12,2+bob),(16,4+bob),(17,8+bob),(18,9+bob),(16,10+bob),(15,13+bob),(11,13+bob),(9,10+bob)],'skin1')
  r(g,14,6+bob,3,4,'skin2');r(g,16,7+bob,1,1,'black')
  poly(g,[(8,6+bob),(8,3+bob),(11,1+bob),(15,2+bob),(17,4+bob),(12,4+bob),(10,8+bob),(10,12+bob),(8,10+bob)],'hair')
  ellipse(g,8,8+bob,2,3,'hair');r(g,10,3+bob,3,1,'brown')
  return flip(g,27) if facing else g
 raise ValueError(kind)

def bag():
 g=Geometry();r(g,0,3,16,11,'wood0');r(g,1,4,14,9,'wood2');r(g,1,4,14,1,'sand')
 for x in [3,11]:r(g,x,4,2,9,'brown');r(g,x,7,2,2,'steel2')
 line(g,(6,3),(6,1),.6,'wood0');line(g,(6,1),(10,1),.6,'wood0');line(g,(10,1),(10,3),.6,'wood0')
 return g

def tree(g,x,y,h=70,seed=1):
 rng=random.Random(seed)
 line(g,(x,y),(x+3,y-h*.63),2,'wood0');line(g,(x,y-4),(x+1,y-h*.64),.8,'wood2')
 for dx,dy,rad in [(-13,-.74,16),(5,-.84,19),(22,-.69,16),(-25,-.56,14),(0,-.6,24),(18,-.48,16)]:
  xx=x+dx;yy=y+h*dy;line(g,(x+2,y-h*.42),(xx,yy),1,'wood1')
  ellipse(g,xx,yy,rad,rad*.65,'metal0');ellipse(g,xx-2,yy-3,rad-3,rad*.49,'green')
  for i in range(16):r(g,xx+rng.randrange(-rad+4,rad-3),yy+rng.randrange(-int(rad*.5),int(rad*.3)),rng.randrange(2,5),1,'metal2')

def cactus(g,x,y,h=24):
 line(g,(x,y),(x,y-h),2,'metal1');line(g,(x-1,y-2),(x-1,y-h+1),.5,'metal3')
 for direction,dy in [(-1,7),(1,3)]:
  line(g,(x,y-h*.5),(x+6*direction,y-h*.5),1.5,'metal1');line(g,(x+6*direction,y-h*.5),(x+6*direction,y-h-dy),1.5,'metal1')
  r(g,x+6*direction-1,y-h-dy,1,7,'metal3')

def house(g,x,y,w=125,h=69):
 r(g,x,y,w,h,'plaster2');r(g,x+w-5,y,5,h,'plaster0')
 poly(g,[(x-10,y+2),(x+19,y-20),(x+w-8,y-20),(x+w+9,y+2)],'red0')
 for yy in range(y-18,y+1,4):
  length=int((yy-(y-20))*.8);xx=x+19-length
  for k in range(xx,x+w-7+length,7):r(g,k,yy,6,3,'clay');r(g,k,yy,6,1,'ochre')
 r(g,x-9,y+1,w+18,3,'wood0');r(g,x-6,y+2,w+11,1,'wood2')
 for xx in [x+10,x+w-25]:
  r(g,xx,y+16,18,23,'wood0');r(g,xx+2,y+18,14,19,'wood1')
  for z in range(xx+3,xx+17,4):r(g,z,y+18,1,19,'wood3')
  r(g,xx-1,y+38,20,3,'plaster0');r(g,xx-1,y+38,20,1,'cream')
 r(g,x+48,y+12,27,h-12,'brown');r(g,x+50,y+14,23,h-14,'wood0');r(g,x+64,y+14,9,h-14,'wood1')
 r(g,x+65,y+14,1,h-14,'wood3');r(g,x+66,y+39,2,2,'gold')
 r(g,x+44,y+h-1,34,3,'plaster0');r(g,x+43,y+h+2,38,3,'clay');r(g,x+43,y+h+2,38,1,'cream')
 rng=random.Random(22)
 for i in range(65):
  xx=rng.randrange(x,x+w);yy=rng.randrange(y+4,y+h)
  if not x+8<xx<x+w-6 or yy>y+h-8:r(g,xx,yy,3,1,'plaster1')
 poly(g,[(x,y+h-16),(x+7,y+h-12),(x+10,y+h),(x,y+h)],'clay')

def village():
 g=Geometry();rng=random.Random(1952)
 r(g,0,0,320,180,'glass1');r(g,0,47,320,30,'glass2')
 for x,y,w in [(12,24,48),(199,18,51),(253,44,41)]:
  ellipse(g,x,y,w,3,'ivory');ellipse(g,x+8,y-3,w*.45,4,'cream')
 poly(g,[(0,80),(27,66),(51,70),(87,57),(134,70),(174,63),(222,74),(273,61),(320,68),(320,113),(0,113)],'plaster1')
 poly(g,[(0,98),(49,86),(95,91),(144,84),(193,93),(248,78),(284,88),(320,91),(320,119),(0,119)],'wood2')
 r(g,0,113,320,67,'floor2');poly(g,[(147,105),(196,105),(292,180),(94,180)],'sand')
 for i in range(210):
  x=rng.randrange(320);y=rng.randrange(110,180);r(g,x,y,rng.choice([1,2,3,5]),1,rng.choice(['floor1','floor3','ochre','sand']))
 tree(g,288,118,103,4);house(g,28,60,132,66)
 for x in range(175,270,12):
  line(g,(x,117),(x+2,97),1.3,'wood1');r(g,x+1,101,1,12,'wood3')
 line(g,(173,105),(271,102),.6,'wood0');line(g,(173,113),(271,111),.6,'wood0')
 # Clothes on a line, jars and an irregular foreground wall.
 line(g,(0,81),(35,85),.6,'wood0')
 for x,c in [(5,'plaster3'),(18,'blue1')]:poly(g,[(x,82),(x+9,83),(x+10,96),(x+2,95)],c)
 g.paste(barrel(14,22),11,109);g.paste(crate(19,12),168,115)
 ellipse(g,25,133,8,3,'floor1');ellipse(g,23,129,5,7,'clay');r(g,20,121,6,2,'ochre');r(g,21,121,4,1,'wood0')
 cactus(g,232,121,21);cactus(g,5,145,29)
 for x,y in [(211,125),(257,139),(277,129),(187,145)]:
  for dx in [-3,0,3]:line(g,(x,y),(x+dx,y-5-abs(dx)),.5,'green')
 poly(g,[(0,155),(27,149),(43,152),(56,159),(55,180),(0,180)],'wood0')
 for x,y,w in [(0,153,16),(18,152,13),(33,157,18),(4,164,26),(32,168,23)]:r(g,x,y,w,6,'plaster0');r(g,x,y,w,1,'plaster2')
 return g

def truck(boards=False):
 g=Geometry()
 if boards:
  for yy in [17,23,29]:plank(g,0,yy,73,5)
  for xx in [1,33,69]:r(g,xx,15,3,21,'wood0');r(g,xx,15,1,20,'wood3')
  return g
 # 1950s open cargo truck, horizontally composed, front at the right.
 r(g,1,28,73,11,'wood0');r(g,3,31,71,5,'wood2');r(g,3,31,71,1,'sand')
 r(g,5,39,103,5,'metal0');r(g,13,42,85,2,'steel0')
 poly(g,[(74,12),(80,5),(96,5),(103,24),(119,27),(122,34),(121,41),(73,41)],'metal0')
 poly(g,[(77,13),(82,7),(94,7),(100,24),(99,39),(77,39)],'metal1')
 r(g,79,13,6,12,'glass0');r(g,80,13,4,2,'glass2')
 poly(g,[(87,10),(94,10),(98,23),(87,23)],'glass0');poly(g,[(88,11),(93,11),(96,20),(88,17)],'glass1')
 r(g,77,5,19,2,'metal3');r(g,76,27,23,2,'metal2');r(g,89,29,5,1,'steel2')
 poly(g,[(101,26),(117,28),(120,31),(120,39),(100,39)],'metal1');r(g,102,27,13,2,'metal3')
 r(g,118,30,4,8,'steel0');r(g,118,30,4,1,'steel2');r(g,119,33,3,1,'black');r(g,119,36,3,1,'black')
 r(g,119,28,3,3,'ivory');r(g,115,38,9,3,'steel1');r(g,73,38,10,3,'steel1')
 r(g,96,19,6,1,'metal0');r(g,101,16,2,6,'steel1');r(g,102,15,3,4,'steel0')
 for xx in [20,100]:
  ellipse(g,xx,43,12,12,'black');ellipse(g,xx,43,9,9,'trouser0');ellipse(g,xx,43,6,6,'steel1');ellipse(g,xx,43,3,3,'steel0')
  r(g,xx-6,35,5,1,'steel0');r(g,xx-3,37,5,1,'steel2')
 return g

def wheel(phase=0):
 g=Geometry();ellipse(g,0,0,5,5,'steel1');ellipse(g,0,0,2,2,'steel0')
 for i in range(3):
  a=phase+i*math.tau/3;r(g,round(3*math.cos(a)),round(3*math.sin(a)),1,1,'steel3')
 return g

def road_sky(night=False):
 g=Geometry();r(g,0,0,320,180,'blue0' if night else 'glass1')
 r(g,0,64,320,36,'blue1' if night else 'glass2')
 if night:
  ellipse(g,259,30,9,9,'cream');ellipse(g,263,27,8,8,'blue0')
  for x,y in [(13,27),(47,41),(71,17),(109,52),(152,22),(183,38),(218,13),(295,48)]:r(g,x,y,1,1,'steel2')
 else:
  ellipse(g,261,31,13,13,'cream')
  for x,y,w in [(57,22,47),(195,49,40)]:ellipse(g,x,y,w,3,'ivory');ellipse(g,x+7,y-3,w*.4,4,'cream')
 return g

def ridges(near=False,night=False):
 g=Geometry();rng=random.Random(20+near)
 pts=[(-30,125)]+[(x,(99 if near else 79)+rng.randrange(-15,9)) for x in range(-30,700,24)]+[(700,142),(-30,142)]
 poly(g,pts,('blue1' if near else 'blue0') if night else ('wood2' if near else 'plaster1'))
 if near:
  for x in range(20,650,48):poly(g,[(x,105),(x+12,91),(x+7,110),(x-15,116)],'steel0' if night else 'ochre')
 return g

def roadside(night=False):
 g=Geometry();rng=random.Random(52);r(g,-10,118,760,62,'blue0' if night else 'floor2')
 r(g,-10,128,760,26,'steel0' if night else 'sand');r(g,-10,128,760,1,'blue1' if night else 'cream')
 for i in range(360):
  x=rng.randrange(740);y=rng.randrange(121,178);r(g,x,y,rng.randrange(1,6),1,('steel1' if night else 'floor3') if y<153 else ('black' if night else 'floor1'))
 for x in range(22,730,90):cactus(g,x,123,18);r(g,x+24,122,7,2,'steel0' if night else 'wood1')
 for x in range(6,730,61):
  for dx in [-4,0,4]:line(g,(x,174),(x+dx,164-abs(dx)),.6,'black' if night else 'metal0')
 return g

def prison():
 g=Geometry();rng=random.Random(2018);r(g,0,0,320,180,'glass0')
 poly(g,[(0,95),(320,83),(320,180),(0,180)],'steel0')
 r(g,52,0,268,114,'plaster1');r(g,57,0,260,112,'plaster2')
 for yy in [21,43,66,90,112]:r(g,57,yy,263,1,'plaster0');r(g,57,yy+1,263,1,'plaster3')
 for xx in [103,157,211,265]:r(g,xx,0,1,112,'plaster0')
 r(g,170,46,74,69,'metal0');r(g,174,49,66,66,'black')
 r(g,202,50,2,64,'steel1');r(g,174,49,65,2,'steel2')
 for x in [72,267]:
  r(g,x,43,29,42,'steel0');r(g,x+3,46,23,35,'glass0')
  for xx in range(x+5,x+26,6):r(g,xx,44,1,40,'steel2')
  r(g,x,65,29,2,'steel1')
 r(g,167,113,80,4,'steel1');r(g,163,117,88,4,'steel0');r(g,159,121,96,4,'steel1')
 r(g,164,117,86,1,'steel2');r(g,159,121,96,1,'steel2')
 # A symbolic federal-police entrance, not a reconstruction of an exact photo.
 r(g,128,21,146,16,'blue0');label(g,'POLÍCIA FEDERAL',137,26,'steel3')
 for i in range(95):r(g,rng.randrange(320),rng.randrange(127,159),rng.randrange(1,5),1,rng.choice(['steel0','steel1','glass0']))
 for x in [-30,68,166,273,383]:line(g,(201+(x-201)*.2,125),(x,179),.6,'trouser0')
 for yy in [139,156,178]:line(g,(0,yy),(320,yy-7),.5,'trouser0')
 # Side fence and foliage frame the walkway.
 tree(g,22,107,101,3)
 for x in range(0,53,8):r(g,x,78,2,55,'metal0');r(g,x,78,1,54,'steel1')
 r(g,0,85,55,2,'steel0');r(g,0,113,55,2,'steel0')
 g.paste(barrel(17,24,'metal0'),281,113)
 r(g,4,143,39,37,'black');r(g,8,139,37,6,'steel0');r(g,8,139,37,1,'steel1')
 r(g,303,0,5,157,'metal0');r(g,304,0,1,156,'steel1')
 return g

def city():
 g=Geometry();rng=random.Random(1956);r(g,0,0,320,180,'glass0')
 for x,h,w in [(2,67,39),(49,93,28),(83,79,34),(121,52,23),(155,70,32),(196,95,29),(243,60,38),(287,84,33)]:
  r(g,x,102-h,w,h,'plaster0');r(g,x+2,104-h,w-4,h-2,'plaster1')
  for yy in range(110-h,93,10):
   for xx in range(x+5,x+w-3,9):r(g,xx,yy,3,5,'steel0')
 # Receding street, shopfronts and a shoeshine stand.
 poly(g,[(0,91),(320,90),(320,180),(0,180)],'floor1')
 poly(g,[(141,97),(188,97),(258,180),(55,180)],'steel0')
 for yy in [110,123,140,159]:
  for xx in range(0,320,18):r(g,xx+(yy%3)*3,yy,14,1,'floor0')
 for x,y,w,h in [(0,28,112,95),(229,37,91,92)]:
  r(g,x,y,w,h,'plaster2');r(g,x+w-5,y,5,h,'plaster0');r(g,x,y+5,w,2,'cream')
  for xx in range(x+11,x+w-12,27):
   r(g,xx,y+15,17,24,'wood0');r(g,xx+2,y+17,13,19,'glass0');r(g,xx+8,y+16,1,22,'metal2');r(g,xx,y+38,18,2,'cream')
  r(g,x+8,y+60,w-16,35,'wood0');r(g,x+12,y+63,w-24,30,'wood1')
  for xx in range(x+18,x+w-14,20):r(g,xx,y+63,12,24,'glass0');r(g,xx,y+63,1,24,'glass1')
  poly(g,[(x-3,y+56),(x+w+2,y+56),(x+w+10,y+66),(x-8,y+66)],'red0')
  for xx in range(x,x+w,14):poly(g,[(xx,y+56),(xx+6,y+56),(xx+8,y+66),(xx-2,y+66)],'plaster3')
  r(g,x,y+67,w,2,'wood0')
 r(g,5,69,101,11,'wood1');label(g,'ARMAZÉM',32,71,'ivory')
 r(g,239,77,72,10,'blue0');label(g,'SAPATOS',254,79,'cream')
 g.paste(crate(23,17),2,116);g.paste(crate(17,13),7,104);g.paste(barrel(17,24),269,114)
 # Electrical lines, tram rail fragments, sidewalk details.
 r(g,207,10,4,112,'wood0');r(g,207,10,1,112,'wood2');r(g,192,22,30,2,'wood0')
 for yy in [21,24]:line(g,(0,yy+10),(201,yy),.5,'wood0');line(g,(201,yy),(320,yy+7),.5,'wood0')
 line(g,(160,101),(122,180),.5,'steel1');line(g,(168,101),(187,180),.5,'steel1')
 for i in range(105):
  x=rng.randrange(320);y=rng.randrange(124,159);r(g,x,y,rng.choice([1,2,3]),1,'floor0')
 g.paste(crate(23,16),298,143);g.paste(barrel(17,26),281,140)
 return g

def chair():
 g=Geometry()
 for x in [0,15]:r(g,x,0,2,34,'wood0');r(g,x,1,1,32,'wood2')
 for y in [2,9,17]:plank(g,0,y,17,3)
 r(g,0,20,20,3,'wood0');r(g,0,20,19,1,'wood3');r(g,17,22,2,12,'wood1')
 return g

def hall(big=False):
 g=Geometry();rng=random.Random(1975);r(g,0,0,320,180,'plaster2')
 r(g,0,0,320,11,'wood0');r(g,0,11,320,3,'wood2');r(g,0,14,320,1,'cream')
 for x in [9,110,212,308]:r(g,x,14,5,94,'plaster1');r(g,x,14,1,94,'cream')
 r(g,0,102,320,10,'wood1');r(g,0,102,320,1,'wood3')
 for x in [23,240]:
  r(g,x,32,53,57,'wood0');r(g,x+3,35,47,51,'glass0')
  for xx in [x+18,x+34]:r(g,xx,34,2,52,'wood1');r(g,xx,34,1,52,'sand')
  for yy in [51,69]:r(g,x+2,yy,49,2,'wood1')
  poly(g,[(x+4,37),(x+13,37),(x+17,85),(x+4,85)],'glass1')
  r(g,x-3,89,59,4,'plaster0');r(g,x-3,89,59,1,'cream')
 if big:
  r(g,83,30,143,43,'wood0');r(g,85,32,139,39,'red0');r(g,87,34,135,1,'red1')
  label(g,'METALÚRGICOS',123,42,'ivory');label(g,'SÃO BERNARDO',122,55,'cream')
 else:
  r(g,124,33,73,55,'wood1');r(g,126,35,69,51,'wood0')
  for x,y,w,h in [(131,41,23,18),(160,39,27,32),(139,65,19,16)]:
   r(g,x,y,w,h,'plaster3')
   for yy in range(y+4,y+h-2,4):r(g,x+3,yy,w-6,1,'plaster1')
  ellipse(g,97,46,8,8,'wood0');ellipse(g,97,46,6,6,'cream');line(g,(97,46),(97,41),.5,'wood0');line(g,(97,46),(101,48),.5,'wood0')
 r(g,0,112,320,68,'floor1')
 for yy in [115,122,133,147,167]:r(g,0,yy,320,1,'floor0');r(g,0,yy+1,320,1,'floor2')
 for yy,offset in [(123,15),(134,40),(148,0)]:
  for xx in range(offset,320,48):r(g,xx,yy,1,12,'floor0')
 for i in range(90):r(g,rng.randrange(320),rng.randrange(116,159),rng.choice([2,3,4]),1,rng.choice(['floor0','floor2']))
 # Ceiling fan and hanging lamps, built into the geometry.
 r(g,156,0,2,17,'wood0');ellipse(g,157,18,5,2,'metal0')
 poly(g,[(151,17),(125,19),(123,22),(151,20)],'steel0');poly(g,[(162,17),(190,15),(192,18),(163,20)],'steel0')
 for x in [80,231]:
  r(g,x,0,1,23,'wood0');poly(g,[(x-2,23),(x+2,23),(x+7,27),(x-7,27)],'metal0');r(g,x-5,27,10,1,'cream')
 if big:
  r(g,51,113,226,6,'wood0');r(g,54,109,220,5,'wood2');r(g,54,109,220,1,'sand')
  # Side curtains leave windows visible and the speaker in a clear silhouette.
  for xx in [2,302]:
   r(g,xx,16,16,96,'red0')
   for k in [3,8,13]:r(g,xx+k,17,2,90,'brown')
 else:
  shelf(g,282,60,34,52);g.paste(crate(18,13),262,101)
 return g

def table():
 g=Geometry();poly(g,[(0,0),(80,0),(86,7),(-5,7)],'wood2');r(g,-5,7,91,3,'wood0');r(g,-5,7,91,1,'sand')
 for x in [1,75]:r(g,x,10,4,22,'wood1');r(g,x,10,1,22,'wood3')
 poly(g,[(13,1),(28,1),(30,5),(15,5)],'ivory');r(g,17,2,10,1,'plaster1')
 r(g,58,-5,4,7,'steel2');r(g,58,-5,4,1,'ivory');r(g,45,0,6,3,'wood0')
 return g

def podium():
 g=Geometry();poly(g,[(0,2),(27,2),(25,30),(2,30)],'wood1');r(g,3,5,20,23,'wood2');r(g,5,5,1,23,'sand')
 r(g,-2,0,31,3,'wood0');r(g,-2,0,31,1,'wood3');r(g,0,30,28,3,'wood0')
 line(g,(20,0),(20,-10),.6,'steel1');line(g,(20,-10),(14,-14),.6,'steel2');r(g,12,-15,5,2,'black')
 return g
