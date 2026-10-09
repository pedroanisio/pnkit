# Quatro maneiras de tocar

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Quatro respostas à mesma luz: ouro, transmissão, papel rugoso e sheen têxtil. Texturas originais procedurais. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** Colher OBJ, copo oco com parede8, água IOR1.33, folha dobrada e pano drapejado; todos na mesa y1425. Vidro IOR1.48, roughness .025.

**Custo medido:** 56.8 fps medidos na RTX 6000 Ada; 1.54 s de encode, sem espera na fila. Still: 1.303 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Água e pano são geometrias estáticas ilustrativas; não são fluidos/soft-body neste exemplo. Refração screen-space não tem cáusticas. Textura das fibras não simula microestrutura.

**Como usar num Short:** Comparar isolamento e reflexão; escolher material de uma cápsula; apresentar amostras antes de uma experiência.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 06-materials/scene.xml --time 1.75 -o 06-materials/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 06-materials/scene.xml -o 06-materials/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
