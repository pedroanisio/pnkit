from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'work/catalog.json').read_text())[8:]
font=ImageFont.truetype(str(root/'assets/atlas.ttf'),16)
for page in range(math.ceil(len(items)/6)):
    selected=items[page*6:page*6+6]; sheet=Image.new('RGB',(900,1100),'#101C2A');d=ImageDraw.Draw(sheet)
    for i,item in enumerate(selected):
        im=Image.open(root/item['slug']/'still.png').convert('RGB');im.thumbnail((288,512));x=(i%3)*300+6;y=(i//3)*550
        sheet.paste(im,(x,y));d.text((x,y+517),item['slug'],font=font,fill='white')
    sheet.save(root/'work'/('STILLS-WAVE2-'+str(page+1)+'.jpg'),quality=95)
