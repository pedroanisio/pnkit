from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];items=json.loads((root/'work/catalog.json').read_text())[8:]
font=ImageFont.truetype(str(root/'assets/atlas.ttf'),22)
for page in range(math.ceil(len(items)/4)):
    sheet=Image.new('RGB',(960,1480),'#101C2A');d=ImageDraw.Draw(sheet)
    for j,item in enumerate(items[page*4:page*4+4]):
        y=j*370;d.text((10,y),item['slug'],font=font,fill='white')
        for i,t in enumerate(['0.25','1.75','3.25']):
            im=Image.open(root/item['slug']/'samples'/('t'+t+'.png')).convert('RGB').crop((0,520,1080,1640));im.thumbnail((308,320));sheet.paste(im,(i*320+6,y+32));d.text((i*320+12,y+342),t+' s',font=font,fill='white')
    sheet.save(root/'work'/('MOTION-WAVE2-'+str(page+1)+'.jpg'),quality=95)
