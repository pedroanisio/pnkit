# Olhe aqui. Agora ali.

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

A mudança de foco transfere a atenção entre objetos em profundidades diferentes.

**Parâmetros:** 85 mm, f/0.7 exagerado para tornar o efeito didático; foco 1250 → 2050 unidades entre 0.5 e 3 s; sete lâminas. Para uso natural, comece em f/1.4–2.

**Custo medido:** 58.0 fps medidos na RTX 6000 Ada; 1.50 s de encode, sem espera na fila. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** DOF afeta object3D; placas 2.5D e texto continuam nítidos. FocalLength substitui o FOV. Checar a legibilidade depois do foco.

**Como usar num Short:** Do componente à máquina; do sintoma à causa no fundo; revelar qual amostra foi selecionada.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 03-dof-focus-pull/scene.xml --time 1.75 -o 03-dof-focus-pull/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 03-dof-focus-pull/scene.xml -o 03-dof-focus-pull/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte DejaVu acompanha seu aviso em assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
