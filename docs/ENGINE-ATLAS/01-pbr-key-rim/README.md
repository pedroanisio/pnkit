# A luz revela os dentes

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Key lateral cria volume, rim frio separa o contorno; o apoio recebe sombra real. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.

[Comparação A/B](COMPARISON.jpg) · [Cena sem o recurso](before.scene.xml)

**Parâmetros:** Engrenagem OBJ original; key200 lateral, rim650 por trás, dome .32; piso200000; shadow2048, contato desligado. A/B isola rim.

**Custo medido:** 58.7 fps medidos na RTX 6000 Ada; 1.48 s de encode, sem espera na fila. Still: 1.297 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Luzes usam metros (100 unidades = 1 m). Área usa aproximação de ponto representativo. Não elevar ambient até apagar o volume. Em planos extensos com câmera rasante, contactShadows pode criar falsa sombra: desligue na luz afetada e preserve castShadow=true. A/B e regiões medidas em ../ISSUES.md, ENGINE-01.

**Como usar num Short:** Revelar um sensor antes de explicar sua função; distinguir duas peças por luz; mostrar o contato que causa uma força.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 01-pbr-key-rim/scene.xml --time 1.75 -o 01-pbr-key-rim/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 01-pbr-key-rim/scene.xml -o 01-pbr-key-rim/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
