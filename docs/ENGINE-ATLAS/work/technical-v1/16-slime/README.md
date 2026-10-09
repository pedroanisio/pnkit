# O caminho se reforça

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Agentes percebem trilhas, depositam sinal e fazem uma rede emergir. É uma execução do modelo abstrato.

**Parâmetros:** 40000 agents, resolution 320, spawn disc, speed 85, saturation 8, seed 3.

**Custo medido:** 35.3 fps medidos na RTX 6000 Ada; 2.41 s de encode, sem espera na fila. Still: 1.117 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Não é reprodução de um resultado biológico específico sem parâmetros/dados. Crescimento longo precisa escala temporal e evidência; CPU e checkpoints crescem.

**Como usar num Short:** Trilhas que se reforçam; redes sem centralização; mostrar a diferença entre explorar e consolidar.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 16-slime/scene.xml --time 3.25 -o 16-slime/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 16-slime/scene.xml -o 16-slime/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte DejaVu acompanha seu aviso em assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
