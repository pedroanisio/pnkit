# A palavra também age

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Três presets com funções distintas: revelar, resolver letras, contar um número com layout tipográfico. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** PresetStart .1, presetDuration 1.8; segurar palavra completa por pelo menos 1.5 s.

**Custo medido:** 61.6 fps medidos na RTX 6000 Ada; 1.40 s de encode, sem espera na fila. Still: 0.664 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Counter interpola números: não usar como contagem real de simulação. Scramble só para revelação, não para informação que precisa ler antes de estabilizar.

**Como usar num Short:** Um termo que emerge de uma forma; descobrir uma sequência; um número que chega ao resultado verdadeiro da narração.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 20-text-animators/scene.xml --time 2.75 -o 20-text-animators/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 20-text-animators/scene.xml -o 20-text-animators/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
