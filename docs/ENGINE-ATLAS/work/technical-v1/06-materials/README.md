# A superfície explica

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Quatro respostas à mesma luz: ouro, transmissão, papel rugoso e sheen têxtil. Texturas originais procedurais.

**Parâmetros:** Metallic 1 / roughness .22; vidro transmission 1 / roughness .025 / ior 1.48; papel .94; tecido sheenRoughness .55.

**Custo medido:** 50.4 fps medidos na RTX 6000 Ada; 1.71 s de encode, sem espera na fila. Still: 1.150 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Papel e tecido são aproximações de superfície; a esfera não demonstra fibras, espessura ou dobra de tecido. Vidro requer algo visível atrás.

**Como usar num Short:** Comparar isolamento e reflexão; escolher material de uma cápsula; apresentar amostras antes de uma experiência.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 06-materials/scene.xml --time 1.75 -o 06-materials/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 06-materials/scene.xml -o 06-materials/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte DejaVu acompanha seu aviso em assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
