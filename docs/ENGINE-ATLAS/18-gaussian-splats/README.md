# Um objeto de pontos

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Seis mil gaussianas formam um anel volumétrico que gira. O asset é sintético e não simula um scan real. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** 6000 splats; scale 1.7; rotationY 0 → 70. Para captura: mesh format ply com f_dc/scale, câmera e escala conferidas.

**Custo medido:** 59.9 fps medidos na RTX 6000 Ada; 1.45 s de encode, sem espera na fila. Still: 1.043 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Splats não recebem nova luz nem projetam sombras. .splat não tem spherical harmonics; captura PLY pode trazer brilho dependente da vista.

**Como usar num Short:** Trazer um artefato capturado para um Short; mostrar uma nuvem volumétrica; comparar captura e reconstrução.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 18-gaussian-splats/scene.xml --time 1.75 -o 18-gaussian-splats/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 18-gaussian-splats/scene.xml -o 18-gaussian-splats/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
