# O tempo atravessa o vidro

![Still](still.png)

Quadro-herói estático; sem clipe necessário.

Quadro de capa com reflexões e iluminação indireta determinísticas. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** Ampulheta OBJ original, vidro e latão; pathSamples128,maxBounces6,denoise; still apenas.

**Custo medido:** Somente still; 51.357 s medidos no servidor 2 (registro da primeira rodada em ISSUES.md). Still: 166.199 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Areia é sólido ilustrativo, não simulação granular. Vidro não gera cáusticas; 128 amostras ainda exigem medir ruído e custo. Nesta versão,128 amostras ainda exibem fireflies/pontos escuros isolados: demonstração técnica, não capa final aprovada.

**Como usar num Short:** Capa de uma peça ou material; comparação de acabamento; revelar uma amostra como objeto de museu.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 05-pathtrace-hero/scene.xml --time 1.75 -o 05-pathtrace-hero/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 05-pathtrace-hero/scene.xml -o 05-pathtrace-hero/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
