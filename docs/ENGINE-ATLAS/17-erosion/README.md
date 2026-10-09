# O relevo guarda o fluxo

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Gotas transportam e depositam sedimento sobre um terreno procedural; a imagem é o hillshade do estado simulado. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** Resolution 192, droplets 16000/s, relief 1.8, seed 5; aumentar resolução só após medir.

**Custo medido:** 51.7 fps medidos na RTX 6000 Ada; 1.66 s de encode, sem espera na fila. Still: 0.707 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Terreno sintético sem geografia real nem escala de tempo física. Poucos segundos mudam detalhes; amplie um trecho para mostrar antes/depois.

**Como usar num Short:** Explicar erosão e depósito; revelar caminhos na paisagem; usar terreno como metáfora de memória.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 17-erosion/scene.xml --time 1.75 -o 17-erosion/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 17-erosion/scene.xml -o 17-erosion/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
