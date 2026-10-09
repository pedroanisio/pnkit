# Mudar tem uma razão

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Três janelas com a mesma mudança de estado: memória/luz, deslocamento e revelação por luminância. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** Duração .85 s centrada em 1.75; whip-pan direction right; luma exige matte node.

**Custo medido:** 61.4 fps medidos na RTX 6000 Ada; 1.41 s de encode, sem espera na fila. Still: 1.203 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Whip-pan é warp 2D, não câmera 3D. Matte nomeia nó, não asset. Em filmes, escolha uma transição pelo sentido da mudança e reveja os frames intermediários.

**Como usar num Short:** Luz que abre um flashback; deslocamento rápido entre duas regiões do mesmo aparelho; revelar segundo estado por sua luminância.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 21-motivated-transitions/scene.xml --time 1.6 -o 21-motivated-transitions/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 21-motivated-transitions/scene.xml -o 21-motivated-transitions/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
