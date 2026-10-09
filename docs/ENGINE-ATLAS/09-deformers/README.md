# A forma respira

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Uma silhueta vetorial é deformada em tempo real; nenhuma sequência de imagens necessária. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** Wave amount 55 px, frequency 2, phase 0 → 360; bend 18°. Use amplitude 10–25 para respirar, 55 para vitrine.

**Custo medido:** 61.1 fps medidos na RTX 6000 Ada; 1.41 s de encode, sem espera na fila. Still: 0.661 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Deformer junto de threeD em camada de imagem/vídeo é ignorado. Valores altos podem dobrar a malha sobre si mesma.

**Como usar num Short:** Bandeira ou membrana; objeto que reage ao calor; transformar a forma para explicar flexibilidade.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 09-deformers/scene.xml --time 1.75 -o 09-deformers/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 09-deformers/scene.xml -o 09-deformers/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
