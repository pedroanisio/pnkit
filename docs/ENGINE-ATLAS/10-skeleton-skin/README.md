# O gesto vem dos ossos

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Uma faixa inteira acompanha uma cadeia de três ossos e mistura pesos entre articulações. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** Três bones de 225 unidades; rotações moderadas -20 → 25 / 20 → -35; pesos automáticos por distância.

**Custo medido:** 60.7 fps medidos na RTX 6000 Ada; 1.44 s de encode, sem espera na fila. Still: 0.659 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Pesos automáticos podem dobrar partes vizinhas indesejadas. Use arquivo weights em JSON para controlar influência; IK precisa alvo e ordem válidos.

**Como usar num Short:** Braço mecânico; caule que cresce e aponta; personagem desenhado que acompanha uma indicação.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 10-skeleton-skin/scene.xml --time 1.75 -o 10-skeleton-skin/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 10-skeleton-skin/scene.xml -o 10-skeleton-skin/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
