# O movimento tem caminho

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

A seta percorre a curva com orientação da tangente e distância uniforme por segundo. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** SVG cubic path, constantSpeed true, autoOrient true; 3.5 s.

**Custo medido:** 62.1 fps medidos na RTX 6000 Ada; 1.39 s de encode, sem espera na fila. Still: 0.661 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Path é coordenada do pai. Orientação pode virar em cúspides; escolha trajeto suave ou remova autoOrient. Rota ilustrativa, sem dado geográfico.

**Como usar num Short:** Percurso de um sinal; material entrando numa máquina; uma rota com posição sincronizada à fala.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 19-motion-path/scene.xml --time 1.75 -o 19-motion-path/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 19-motion-path/scene.xml -o 19-motion-path/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
