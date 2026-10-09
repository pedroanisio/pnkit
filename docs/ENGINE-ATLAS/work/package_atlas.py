from pathlib import Path
import json,hashlib,subprocess,math,sys
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1]
items=json.loads((root/'work/catalog.json').read_text())
if '--wave1' in sys.argv: items=items[:8]
font=ImageFont.truetype(str(root/'assets/atlas.ttf'),19)
sheet=Image.new('RGB',(4*290,math.ceil(len(items)/4)*575),'#101C2A'); draw=ImageDraw.Draw(sheet)
hashes=[]; qa=[]
for i,item in enumerate(items):
    folder=root/item['slug']; still=folder/'still.png'
    if not still.exists(): continue
    if item['slug']=='01-pbr-key-rim':
        item['limits']+=' Em planos extensos com câmera rasante, contactShadows pode criar falsa sombra: desligue na luz afetada e preserve castShadow=true. A/B e regiões medidas em ../ISSUES.md, ENGINE-01.'
    thumbnail=Image.open(still).convert('RGB'); thumbnail.thumbnail((270,480)); thumbnail.save(folder/'thumb.jpg',quality=93)
    xx=(i%4)*290+10; yy=(i//4)*575+8; sheet.paste(thumbnail,(xx,yy));draw.text((xx,yy+487),item['slug'][:25],font=font,fill='#F4EFE4')
    render_log=(folder/'render.log').read_text()
    report={}
    if (folder/'encode.json').exists():
        try: report=json.loads((folder/'encode.json').read_text())
        except ValueError: pass
    fps=report.get('render_fps'); cost=f'{fps:.1f} fps medidos na RTX 6000 Ada; {report.get("seconds",0):.2f} s de encode, sem espera na fila.' if fps else 'Somente still; 51.357 s medidos no servidor 2 (registro da primeira rodada em ISSUES.md).'
    if (folder/'still-metrics.json').exists():
        measured=json.loads((folder/'still-metrics.json').read_text())
        cost+=f' Still: {measured["wall_seconds"]:.3f} s no servidor 2, medidos em still-metrics.json.'
    if item['slug']=='22-audio-reactive':
        cost+=' O still é um quadro decodificado do clipe com análise de áudio.'
    still_command=f'SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render {item["slug"]}/scene.xml --time {item["still"]} -o {item["slug"]}/still.png --strict --quality final < /dev/null'
    if item['slug']=='22-audio-reactive':
        still_command=f'SR_AGENT=cx-engine ~/videos/tools/sr-remote ffmpeg -nostdin -v error -threads 2 -ss 1.833333 -i {item["slug"]}/clip.mp4 -frames:v 1 -y {item["slug"]}/still.png < /dev/null'
    clip='[Clipe de 3.5 s](clip.mp4)' if (folder/'clip.mp4').exists() else 'Quadro-herói estático; sem clipe necessário.'
    (folder/'README.md').write_text(f'''# {item['title']}

![Still](still.png)

{clip}

{item['notes']}

{('[Comparação A/B](COMPARISON.jpg) · [Cena sem o recurso](before.scene.xml)' if (folder/'COMPARISON.jpg').exists() else '')}

**Parâmetros:** {item['params']}

**Custo medido:** {cost} Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** {item['limits']}

**Como usar num Short:** {item['ideas']}

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
{still_command}
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode {item['slug']}/scene.xml -o {item['slug']}/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
''')
    for name in ['scene.xml','still.png','clip.mp4','README.md','encode.json','before.scene.xml','before.png','COMPARISON.jpg','MOTION-SAMPLES.jpg','count-check.json']:
        p=folder/name
        if p.exists(): hashes.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root)))
    if (folder/'clip.mp4').exists():
        p=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames,r_frame_rate:format=duration','-of','json',str(folder/'clip.mp4')],capture_output=True,text=True,stdin=subprocess.DEVNULL)
        info=json.loads(p.stdout); stream=info['streams'][0]
        valid=stream['width']==1080 and stream['height']==1920 and stream['nb_read_frames']=='84' and stream['r_frame_rate']=='24/1' and abs(float(info['format']['duration'])-3.5)<.001
        qa.append(dict(slug=item['slug'],video=info,technical_pass=valid,strict_clean=bool(report) and not any(report.get(k) for k in ['unsupported','evaluation_warnings','warnings','accessibility'])))
sheet.save(root/'CONTACT-SHEET.jpg',quality=95)
(root/'work/video-checks.json').write_text(json.dumps(qa,indent=2))
intro='''# Atlas visual do rs-scene-render

Exemplos de direção de arte por `cx-engine`, tarefa `engine-atlas-001`. Build `scene-render-premium-f4b4b95bf192`, SHA256 `f4b4b95bf192bedf12af9f3897c7aadb8a8be887a8d380aafc6010aa25f35679`.

Cada pasta traz cena XML, still de vitrine em **1080×1920**, miniatura, parâmetros, limites e usos em Shorts. Recursos de movimento incluem um clipe de **3.5 s / 24 fps / 84 quadros**. Abra o still completo para julgar detalhes; as miniaturas servem à navegação.

![Folha geral](CONTACT-SHEET.jpg)

O atlas demonstra recursos, não determina o look dos filmes. Escolha um avanço que explique melhor a ideia e compare com `../shorts/REFERENCE-LOOK/`; o uso de 3D ou mais efeitos não garante qualidade. Fontes embarcadas, assets procedurais originais e uma fixture DEM sintética do motor, sem downloads pagos. Não contém destinos de upload.

| Miniatura | Recurso | Cena / clipe |
|---|---|---|
'''
for item in items:
    slug=item['slug']; clip=f'[clipe]({slug}/clip.mp4)' if (root/slug/'clip.mp4').exists() else 'still'
    intro+=f'| ![]({slug}/thumb.jpg) | [{item["title"]}]({slug}/README.md) | [XML]({slug}/scene.xml) · {clip} |\n'
intro+='''
Verificação: `work/video-checks.json` registra contagem decodificada, dimensões e resultado strict; `SHA256SUMS` identifica esta entrega. Stills foram renderizados no servidor 2; clipes na RTX do servidor 1, um job por vez via sr-gpu, com a taxa confirmada na conclusão de cada encode curto (todos inferiores a um minuto de render). Custos incluem inicialização e variam por cena/host.

Limitações: inspeção visual de stills e amostras codificadas; não ouvi nem assisti os clipes em movimento. A arte deve julgar cadência, foco e composição em playback antes de integrar. Não há scorecard de publicação para estas demonstrações. Pontos que exigem cuidado estão em [ISSUES.md](ISSUES.md).

Diagnóstico de contato rasante: [A/B completo e mínimo](work/contact-shadow-repro/COMPARISON.jpg) · [regiões medidas](work/contact-shadow-repro/metrics.json). `contactShadows=false` na luz afetada preserva as sombras de shadow map; não compense elevando exposição.

Contagem: [ondas12→96,23 selecionadas,365 peças reais](26-rich-2d-count/count-check.json), vitrine da rotaA aprovada pela arte em REVIEW26-r3. Áudio: [pulso no arquivo codificado](work/audio-count-checks.json). O exemplo 22 usa um still extraído do encode para preservar a análise do áudio; o render isolado não a prepara.
'''
(root/'README.md').write_text(intro)
for p in sorted((root/'assets').iterdir()):
    if p.is_file(): hashes.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root)))
for name in ['README.md','CONTACT-SHEET.jpg','ISSUES.md','work/catalog.json','work/video-checks.json','work/sampling.json','work/audio-count-checks.json','work/final-validation.json','work/comparisons.json','work/contact-shadow-repro/COMPARISON.jpg','work/contact-shadow-repro/metrics.json']:
    p=root/name
    if p.exists(): hashes.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+name)
(root/'SHA256SUMS').write_text('\n'.join(hashes)+'\n')
print('Pacote:',len(items),'cenas;',len(qa),'clipes;',all(x['technical_pass'] and x['strict_clean'] for x in qa))
