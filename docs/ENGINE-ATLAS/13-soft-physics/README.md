# A matéria cede

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Pano preso pela borda esquerda e gel que cai: ambos deformam a própria superfície por simulação. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** Cloth 8×16, stiffness 180, mass 3, pin left; jelly 6×6, stiffness 220, pressure 45.

**Custo medido:** 60.9 fps medidos na RTX 6000 Ada; 1.42 s de encode, sem espera na fila. Still: 0.700 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Molas explícitas exigem substeps; malha muito densa e stiffness alto podem ser recusados (P01). Soft colide com rigid, mas não o empurra.

**Como usar num Short:** Rede que cede com peso; tecido num fluxo; gel absorvendo um impacto.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 13-soft-physics/scene.xml --time 1.75 -o 13-soft-physics/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 13-soft-physics/scene.xml -o 13-soft-physics/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
