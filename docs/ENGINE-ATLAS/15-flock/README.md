# A ordem é local

![Still](still.png)

[Clipe de 3.5 s](clip.mp4)

Seiscentos agentes seguem regras locais; a organização nasce da simulação, não de trajetórias pré-desenhadas. Vitrine revisada: Archivo, subtítulo36 e assunto próprio. Vitrine revisada: Archivo, subtítulo36 e assunto próprio.



**Parâmetros:** 600 agentes, perception 65, separation 1.5, alignment 1.2, cohesion .8; seed 7.

**Custo medido:** 60.9 fps medidos na RTX 6000 Ada; 1.42 s de encode, sem espera na fila. Still: 0.724 s no servidor 2, medidos em still-metrics.json. Cada clipe tem 84 quadros, 1080×1920, 24 fps, quality final. `encode.json` guarda adaptador, warnings, estágios e FPS; `render.log` guarda o still.

**Limites e armadilhas:** Flock representa regras abstratas; não chamar de comportamento medido de animais. Count grande pode pesar na busca de vizinhos.

**Como usar num Short:** Coordenação sem líder; migração ilustrada; formar uma população que se organiza.

```bash
# Dentro de /home/pals/videos/ENGINE-ATLAS, still no servidor 2:
SR_AGENT=cx-engine ~/videos/tools/sr-remote ~/.local/share/scene-render/bin/scene-render-premium render 15-flock/scene.xml --time 1.75 -o 15-flock/still.png --strict --quality final < /dev/null
# Clipe (quando há movimento), uma chamada própria à fila:
SR_AGENT=cx-engine SR_GPU_SHORT=1 ~/.local/share/scene-render/bin/sr-gpu ~/.local/share/scene-render/bin/scene-render-premium encode 15-flock/scene.xml -o 15-flock/clip.mp4 --hw nvenc --parallel 1 --strict --no-upload --quality final --json < /dev/null
```

Mantenha a pasta `../assets` ao copiar a cena. Os assets procedurais foram criados nesta sessão; o DEM sintético foi copiado da fixture de teste do motor e a fonte Archivo acompanha a licença OFL em assets/OFL-archivo.txt. A fonte DejaVu está preservada apenas no histórico técnico, com assets/FONT-LICENSE.txt. Este exemplo é uma ferramenta de direção de arte, sem narração e sem aprovação para publicação. A inspeção de stills e a amostragem do arquivo codificado não substituem avaliação do movimento em playback.
