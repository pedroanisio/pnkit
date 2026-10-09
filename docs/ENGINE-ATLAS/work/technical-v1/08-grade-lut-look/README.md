# Uma paleta, vários materiais

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

LUT suave dá tons âmbar e ciano; AgX controla highlights. A LUT foi criada para esta demonstração.

**Parâmetros:** LUT mix .65 em sRGB; AgX exposure +.3; compare com 01 antes de adotar.

**Custo medido:** 59.0 fps medidos na RTX 6000 Ada; 1.47 s de encode, sem espera na fila. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Espaço errado da LUT muda contraste/cor. AgX altera a imagem global, incluindo títulos; não tentar recuperar luz achatada com grade.

**Como usar num Short:** Unificar foto e modelo; estabelecer a paleta do mundo do Short; diferenciar dois estados de uma experiência.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 08-grade-lut-look/scene.xml --time 1.75 -o 08-grade-lut-look/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 08-grade-lut-look/scene.xml -o 08-grade-lut-look/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte DejaVu acompanha seu aviso em assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
