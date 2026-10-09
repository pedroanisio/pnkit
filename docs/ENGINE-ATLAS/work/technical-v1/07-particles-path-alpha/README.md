# A atmosfera tem origem

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Um caminho emite poeira; a silhueta opaca de um asset emite bokeh. Ambos usam seeds fixos.

**Parâmetros:** Poeira 110/s, size 4, opacity .55; bokeh 12/s, size 14 → 12 ±5, opacity .25; preroll 2–3 s.

**Custo medido:** 61.7 fps medidos na RTX 6000 Ada; 1.40 s de encode, sem espera na fila. Still: 0.721 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Partículas são 2D e não recebem DOF físico. Os presets substituem atributos que ficam no default do schema: declare sizeEnd explicitamente para evitar discos gigantes. Alpha do asset define nascimentos; sprite preserva cor própria.

**Como usar num Short:** Resíduos saindo de uma peça; poeira de uma ruína recortada; mostrar trajetória por material suspenso.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 07-particles-path-alpha/scene.xml --time 1.75 -o 07-particles-path-alpha/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 07-particles-path-alpha/scene.xml -o 07-particles-path-alpha/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte DejaVu acompanha seu aviso em assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
