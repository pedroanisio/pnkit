# O look muda a leitura

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

LUT suave dá tons âmbar e ciano; AgX controla highlights. A LUT foi criada para esta demonstração. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.

[Comparação A/B](COMPARISON.jpg) · [Cena sem o recurso](before.scene.xml)

**Parâmetros:** LUT .cube17³ mix1, working linear-srgb, AgX exposure.3; comparação com a mesma cena sem LUT.

**Custo medido:** 56.0 fps medidos na RTX 6000 Ada; 1.56 s de encode, sem espera na fila. Still: 1.829 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Espaço errado da LUT muda contraste/cor. AgX altera a imagem global, incluindo títulos; não tentar recuperar luz achatada com grade.

**Como usar num Short:** Unificar foto e modelo; estabelecer a paleta do mundo do Short; diferenciar dois estados de uma experiência.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 08-grade-lut-look/scene.xml --time 1.75 -o 08-grade-lut-look/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 08-grade-lut-look/scene.xml -o 08-grade-lut-look/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
