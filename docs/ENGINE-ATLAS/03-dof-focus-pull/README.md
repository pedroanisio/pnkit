# O foco escolhe a peça

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

A mudança de foco transfere a atenção entre objetos em profundidades diferentes. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** 50mm, f/2.2, focus52→325 unidades (0.52→3.25m); três peças em profundidades físicas distintas, pedestais sobre a mesa. 100 unidades=1m.

**Custo medido:** 56.7 fps medidos na RTX 6000 Ada; 1.53 s de encode, sem espera na fila. Still: 1.306 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** DOF apenas object3D. A cena usa escala próxima da lente para círculo de confusão claramente visível; peças traseiras recebem escala maior para comparação de foco.

**Como usar num Short:** Do componente à máquina; do sintoma à causa no fundo; revelar qual amostra foi selecionada.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 03-dof-focus-pull/scene.xml --time 1.75 -o 03-dof-focus-pull/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 03-dof-focus-pull/scene.xml -o 03-dof-focus-pull/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
