"""Original native geometry for the expanded documentary. No raster inputs."""
import math, random
from .geometry import Geometry
from .scene_art import P,FONT,r,poly,line,ellipse,lettering,shelf,crate,barrel,plank
from .story_art import flip,tree,table,chair,city
from .chapter_art import actor as base_actor,home,office,campaign,congress,planalto,stf,papers

FONT.update({
 '$':['00100','01111','10100','01110','00101','11110','00100'],
 'º':['111','101','111','000','111','000','000'],
 '%':['11001','11010','00010','00100','01000','01011','10011'],
 '+':['00000','00100','00100','11111','00100','00100','00000'],
 '/':['00001','00001','00010','00100','01000','10000','10000'],
 '(':['001','010','100','100','100','010','001'],
 ')':['100','010','001','001','001','010','100'],
 '>':['10000','01000','00100','00010','00100','01000','10000'],
 '—':['00000','00000','00000','11111','00000','00000','00000']})

def label(g,txt,x,y,c='cream'):
 q,_=lettering(txt,c);g.paste(q,x,y);return g

def actor(kind,pose='idle',phase=0,facing=False,gesture=.5):
 if kind not in ['cunha','temer','alckmin','moro','deltan','jair','flavio','daughter']:
  return base_actor(kind,pose,phase,facing,gesture)
 if kind=='daughter':
  g=base_actor('mother',pose,phase,False,gesture)
  g.cells={xy:({P['metal1']:P['blue1'],P['metal2']:P['blue2'],P['plaster3']:P['trouser1']}.get(c,c)) for xy,c in g.cells.items()}
  return flip(g,27) if facing else g
 g=base_actor('alencar',pose,phase,False,gesture)
 bob=round(.6*(1-math.cos(phase*2))) if pose=='walk' else 0
 hair='hair' if kind in ['moro','deltan','jair','flavio'] else 'steel1'
 poly(g,[(9,4+bob),(11,1+bob),(16,1+bob),(19,4+bob),(18,7+bob),(15,5+bob),(11,7+bob)],hair)
 r(g,10,3+bob,6,1,'steel2' if kind in ['temer','cunha'] else 'brown')
 if kind=='alckmin':
  r(g,12,2+bob,5,3,'skin2');r(g,10,4+bob,2,3,'steel2')
 if kind in ['cunha','alckmin','deltan']:
  r(g,14,6+bob,4,3,'wood0');r(g,15,7+bob,2,1,'skin2');r(g,12,7+bob,2,1,'wood0')
 if kind in ['jair','flavio']:r(g,13,17+bob,2,7,'blue2' if kind=='jair' else 'gold')
 if kind=='moro':
  for (x,y),c in list(g.cells.items()):
   if 16<=y<=31 and c in [P['blue0'],P['blue1'],P['blue2']]:g.cells[x,y]=P['black']
 if kind=='temer':r(g,18,8+bob,2,2,'skin2')
 return flip(g,27) if facing else g

def neighborhood(w=560,year=2003):
 g=Geometry();rng=random.Random(32);r(g,0,0,w,180,'glass1')
 for x in range(0,w,64):
  h=rng.randrange(30,60);r(g,x,68-h,50,h+40,'steel1')
  for y in range(72-h,80,10):
   for xx in range(x+5,x+45,9):r(g,xx,y,4,5,'glass0')
 r(g,0,129,w,51,'floor1');r(g,0,137,w,4,'plaster2');r(g,0,141,w,39,'steel0')
 for x in range(0,w,38):r(g,x,157,17,2,'plaster3')
 for j,(x,ww,name) in enumerate([(0,103,'OFICINA'),(113,129,'MERCEARIA'),(250,91,'CASA'),(352,131,'ESCOLA'),(493,80,'CAFÉ')]):
  r(g,x,43,ww,87,'plaster2' if j%2 else 'brick');r(g,x,42,ww,4,'wood0')
  r(g,x+4,48,ww-8,12,'metal0');label(g,name,x+(ww-lettering(name)[1])//2,51,'cream')
  r(g,x+12,70,28,60,'wood0');r(g,x+15,73,22,54,'wood1');r(g,x+33,101,2,3,'gold')
  if ww>90:
   r(g,x+49,70,ww-58,41,'wood0');r(g,x+52,73,ww-64,35,'glass0')
   r(g,x+51,89,ww-61,2,'wood2');r(g,x+67,73,2,35,'wood2');r(g,x+46,111,ww-51,3,'cream')
  for y in range(63,127,9):
   for xx in range(x+1,x+ww-2,13):
    if not(x+9<xx<x+43 or x+46<xx<x+ww-7 and y<115):r(g,xx,y,6,1,'clay' if j%2==0 else 'plaster1')
  if j in [1,3]:
   for k in range(0,ww,8):r(g,x+k,60,8,6,'cream' if k%16 else 'red1')
 tree(g,343,135,66,9);g.paste(crate(19,14),90,121);g.paste(barrel(18,24),503,113)
 return g

def employment():
 g=office();r(g,74,24,166,80,'plaster2')
 r(g,90,32,127,24,'metal0');label(g,'AGÊNCIA DE EMPREGO',99,39,'cream')
 for x in [96,130,164,198]:
  r(g,x,70,20,23,'ivory');r(g,x+3,75,14,1,'steel1');r(g,x+3,81,11,1,'steel1')
 r(g,13,35,64,77,'blue0');label(g,'VAGAS',31,45,'cream')
 for yy in [65,77,89]:r(g,22,yy,45,1,'steel2')
 return g

def family_room():
 g=home()
 r(g,264,29,45,85,'wood0');r(g,267,32,39,79,'wood1');r(g,270,35,33,73,'wood2')
 for x in range(272,304,8):r(g,x,36,1,71,'wood3')
 r(g,270,68,3,6,'gold')
 # Small kitchen counter, kept clear of the central table.
 r(g,13,109,58,32,'plaster2');r(g,12,106,60,4,'steel1');r(g,17,113,25,25,'wood1')
 r(g,45,113,21,25,'wood0');r(g,48,116,15,13,'black')
 ellipse(g,30,105,9,2,'metal0');r(g,24,97,13,8,'steel0');r(g,22,97,17,2,'steel2')
 return g

def pot(full=True):
 g=Geometry();ellipse(g,0,0,13,3,'black');r(g,-12,-7,25,8,'steel0');ellipse(g,0,-7,13,3,'steel1')
 ellipse(g,0,-8,10,2,'cream' if full else 'black');r(g,-17,-6,5,3,'black');r(g,12,-6,5,3,'black')
 return g

def corridor():
 g=Geometry();r(g,0,0,400,180,'plaster1');r(g,0,112,400,68,'floor1')
 for y in [119,134,153]:r(g,0,y,400,1,'floor0')
 for x in range(15,400,80):
  r(g,x,27,61,91,'plaster3');r(g,x+4,30,53,88,'wood0');r(g,x+8,35,45,80,'wood1')
  r(g,x+12,38,37,74,'wood2');r(g,x+16,76,3,7,'gold');r(g,x+10,18,42,7,'steel0')
  r(g,x-8,0,3,115,'plaster0')
 r(g,0,8,400,4,'cream')
 return g

def lectern_room(chamber='CÂMARA'):
 g=congress();r(g,93,29,133,41,'blue0');label(g,chamber,160-lettering(chamber)[1]//2,39,'cream')
 r(g,124,75,71,32,'wood0');r(g,123,74,73,3,'wood3');r(g,129,81,61,23,'wood1')
 return g

def document(header='STF',case='HC 193726',year='2021'):
 g=papers();r(g,66,28,168,101,'ivory')
 label(g,header,152-lettering(header)[1]//2,37,'wood0');label(g,case,152-lettering(case)[1]//2,52,'wood1')
 for yy,w in [(66,125),(72,143),(79,114),(112,124)]:r(g,77,yy,w,1,'plaster2')
 label(g,year,140,123,'wood1')
 return g

def newsroom():
 g=Geometry();r(g,0,0,320,180,'blue0');r(g,0,121,320,59,'floor0')
 for x in [16,260]:shelf(g,x,30,45,79)
 for x in [82,180]:
  r(g,x,39,70,51,'black');r(g,x+3,42,64,44,'blue1');r(g,x+33,90,5,12,'steel0');r(g,x+20,101,31,3,'steel1')
  for y in range(51,79,7):r(g,x+9,y,43-(y%4)*3,1,'steel3')
 r(g,65,111,191,5,'wood2');r(g,71,116,6,40,'wood1');r(g,242,116,6,40,'wood1')
 for x in [90,189]:poly(g,[(x,103),(x+38,103),(x+44,109),(x-4,109)],'steel1')
 r(g,267,112,32,2,'cream');r(g,268,109,26,2,'plaster3')
 return g

def court():
 g=Geometry();r(g,0,0,320,180,'plaster2');r(g,0,112,320,68,'floor1')
 for x in [6,308]:r(g,x,0,5,119,'wood2')
 r(g,114,30,91,45,'wood1');r(g,117,33,85,39,'wood0');label(g,'JUSTIÇA',140,47,'cream')
 for x in [25,235]:
  r(g,x,116,60,4,'wood2');r(g,x+4,120,4,34,'wood0');r(g,x+52,120,4,34,'wood0')
 r(g,125,93,70,28,'wood1');r(g,122,91,76,4,'wood2')
 line(g,(159,22),(159,37),1,'gold');line(g,(144,27),(174,27),.6,'gold')
 for x in [144,174]:line(g,(x,27),(x-6,36),.6,'gold');line(g,(x,27),(x+6,36),.6,'gold');line(g,(x-6,36),(x+6,36),.6,'gold')
 return g

def attack():
 g=planalto();rng=random.Random(8)
 for x in [61,112,172,221,279]:
  for i in range(4):
   xx=x+rng.randrange(-5,7);yy=rng.randrange(65,97);line(g,(xx,yy),(xx+5,yy+6),.7,'black')
 for i in range(75):
  x=rng.randrange(32,300);y=rng.randrange(119,157);r(g,x,y,rng.randrange(1,4),1,rng.choice(['glass2','steel2','wood1']))
 return g

def voting():
 g=Geometry();r(g,0,0,320,180,'plaster2');r(g,0,111,320,69,'floor1')
 r(g,14,24,63,65,'wood0');r(g,18,28,55,56,'glass1');r(g,43,28,2,56,'wood1');r(g,18,53,55,2,'wood1')
 r(g,262,27,44,84,'wood0');r(g,265,30,38,81,'wood1')
 r(g,94,28,143,23,'metal0');label(g,'SEÇÃO ELEITORAL',121,35,'cream')
 g.paste(table(),94,116)
 r(g,206,66,36,70,'ivory');poly(g,[(206,66),(217,74),(217,143),(206,136)],'plaster3')
 label(g,'VOTO',211,81,'wood0');r(g,185,110,17,17,'steel2');r(g,186,111,10,9,'blue0')
 for x in [198,201]:
  for y in [112,115,118,121]:r(g,x,y,1,1,'black')
 return g
