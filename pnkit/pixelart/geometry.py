"""Procedural geometry quantized to square cells; emits native XML vector paths.
No image input, image library, bitmap export, atlas or imported character art.
"""
import math, random
from collections import defaultdict
INK='#16242d'; SKIN='#cf9465'; LIT='#efba83'; SHADE='#965f48'
class Geometry:
 def __init__(self):self.cells={}
 def rect(self,x,y,w,h,c):
  for yy in range(round(y),round(y+h)):
   for xx in range(round(x),round(x+w)):self.cells[xx,yy]=c
  return self
 def poly(self,pts,c):
  for y in range(math.floor(min(p[1] for p in pts)),math.ceil(max(p[1] for p in pts))):
   fy=y+.5;cross=[]
   for a,b in zip(pts,pts[1:]+pts[:1]):
    if (a[1]<=fy<b[1]) or (b[1]<=fy<a[1]):cross.append(a[0]+(fy-a[1])*(b[0]-a[0])/(b[1]-a[1]))
   cross.sort()
   for x1,x2 in zip(cross[::2],cross[1::2]):self.rect(math.ceil(x1-.5),y,max(0,math.ceil(x2-.5)-math.ceil(x1-.5)),1,c)
  return self
 def ellipse(self,cx,cy,rx,ry,c):
  for y in range(math.floor(cy-ry),math.ceil(cy+ry)):
   dy=(y+.5-cy)/ry
   if abs(dy)<1:
    dx=rx*math.sqrt(1-dy*dy);self.rect(math.ceil(cx-dx-.5),y,max(0,math.ceil(cx+dx-.5)-math.ceil(cx-dx-.5)),1,c)
  return self
 def line(self,a,b,r,c):
  dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy)
  if ln:
   nx=-dy/ln*r;ny=dx/ln*r
   self.poly([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)],c)
  self.ellipse(*a,r,r,c);self.ellipse(*b,r,r,c)
  return self
 def paste(self,other,x=0,y=0):
  for (xx,yy),c in other.cells.items():self.cells[round(xx+x),round(yy+y)]=c
  return self
 def outline(self,c=INK):
  border={}
  for x,y in self.cells:
   for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if (xx,yy) not in self.cells:border[xx,yy]=c
  border.update(self.cells);self.cells=border;return self
 def scale(self,s=1,flip=False):
  q=Geometry()
  for (x,y),c in self.cells.items():
   if flip:x=79-x
   q.rect(x*s,y*s,s,s,c)
  return q
 def paths(self,unit=4):
  """Merge same-colour cell runs into rectangles, then batch by colour."""
  rows=defaultdict(list)
  for (x,y),c in self.cells.items():rows[(y,c)].append(x)
  bands=defaultdict(list)
  for (y,c),xs in rows.items():
   xs.sort();a=last=xs[0]
   for x in xs[1:]:
    if x==last+1:last=x
    else:bands[(c,a,last+1)].append(y);a=last=x
   bands[(c,a,last+1)].append(y)
  paths=defaultdict(list)
  for (c,x1,x2),ys in bands.items():
   ys.sort();a=last=ys[0]
   def write(y1,y2):
    x=x1*unit;y=y1*unit;w=(x2-x1)*unit;h=(y2-y1)*unit
    paths[c].append(f'M{x},{y}h{w}v{h}h{-w}Z')
   for y in ys[1:]:
    if y==last+1:last=y
    else:write(a,last+1);a=last=y
   write(a,last+1)
  return {c:''.join(p) for c,p in paths.items()}

