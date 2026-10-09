# O dado ocupa a tela

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

As barras e a curva são dados nativos, revelados por progress. Valores sintéticos para ensino de layout.

**Parâmetros:** progress 0 → 1 em 2.7 s; showAxes true, showValues true para barras; largura820.

**Custo medido:** 60.5 fps medidos na RTX 6000 Ada; 1.43 s de encode, sem espera na fila. Still: 0.657 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Animação draw-on não é crescimento observado. Identificar unidade/escala e fonte no filme; labels do gráfico não têm collision pass avançado.

**Como usar num Short:** Diferença entre cenários; uma curva como objeto central do Short; comparação antes/depois sincronizada à frase.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 24-animated-charts/scene.xml --time 3 -o 24-animated-charts/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 24-animated-charts/scene.xml -o 24-animated-charts/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte DejaVu acompanha seu aviso em assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
