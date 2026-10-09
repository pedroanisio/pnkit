# S25 — ENGINE-02: custo de planejamento dos objetos invisíveis

Diagnóstico cx-engine, 2026-10-02 16:03:56 UTC, pedido DECISION UID54 e instrução direta do usuário. Sem alteração do motor, do filme, dos pins ou de jobs de terceiros. Cópia isolada em ENGINE-ATLAS/work/s25-repro; stills/benchmarks no servidor2 via sr-remote, usando premium SHA256f4b4b95bf192bedf12af9f3897c7aadb8a8be887a8d380aafc6010aa25f35679. Cena original SHA2563b6b7483478008f02d8a01d94dcadd2ccd3a3bf3e085f330bcce123f4f5127b5 confirmado inalterado neste instante.

Conclusão: os objetos com opacidade zero NÃO são desenhados na GPU. O compositor ainda paga um custo significativo ao percorrer esses milhares de nós. É uma ineficiência de planejamento/render do motor reproduzida, não um defeito de imagem causado pelo desenho de meshes invisíveis. A enumeração repetida de irmãos 3D em three_members, chamada por cada object3D antes de verificar o primeiro membro, é a causa indicada pelo fonte: custo quadrático no tamanho do bloco. Opacity0 só é descartada posteriormente, antes de object_draws. Não foi coletado perfil de pilha na NVIDIA; não atribuo todo o tempo RTX exclusivamente a este trecho.

No quadro t=0,5s o FrameGraph tem3921 objetos3D,3872 com world_opacity0 e49 positivos. Mesmo com todos presentes, stats.objects3d=49 e2317104 triângulos. Retirar somente os3872 invisíveis da cópia preserva49draws, triângulos e todos os bytes RGBA. A parede do prato usa34 torus com segments256, além de outros elementos visíveis; continua sendo uma imagem com2,3milhões de triângulos. Não propus reduzir subdivisão/material/câmera porque mudaria a imagem aprovada.

Medições: seis quadros15..20 (0,5..0,6667s), duas passagens de warmup do CLI, Vulkan llvmpipe,1080×1920,quality final, --strict --stats. Os tempos são medianas reportadas pelo binário; GPU aqui significa rasterização em software, não uma RTX.

| Variante | Nós object3D no quadro0,5 | Draws3D | CPU planejamento/submissão | Avaliação | GPU software | Render até drenagem |
|---|---:|---:|---:|---:|---:|---:|
| original |3921|49|239,499ms|12,388ms|1136,764ms|1379,963ms|
| removidos somente zeros |49|49|7,365ms|0,101ms|1163,853ms|1172,259ms|
| contorno condition |49|49|7,972ms|10,182ms|1150,486ms|1159,609ms|

Contorno concreto: `condition.scene.xml` conserva todos os objetos, seus materiais, posições, índices de instância, bloco/ordem3D e animações. Acrescenta só condition em78 object3D, derivada das janelas positivas da animação de opacidade ou da mesma expressão de opacidade. Como condition exclui o nó do FrameGraph antes do planejamento, não há lista enorme de irmãos na abertura. Exemplos testados:

```xml
<!-- Mantém850 instâncias e animações originais. -->
<object3D id="cellsA" instances="850" condition="(time >= 23.826 && time <= 52)" .../>
<!-- No XML real && é escapado como &amp;&amp;. -->
```

A lista exata em conditions.json é melhor para integrar do que substituir cegamente o filme inteiro: o produtor copia só os atributos condition para a cena canônica se a arte aceitar. Nas bordas das animações os intervalos são conservadores: podem manter alguns nós já transparentes num instante exato, para nunca remover um positivo. Não muda a contagem científica nem a distribuição dos1700 organismos. Não mude instances para diminuir quantidade: o atributo atual expande nós e não promete uma única drawcall.

Provas:20 tempos0,0.5,13.19,13.24,14,16.555,21.5,23.826,24,24.326,25.3,33.8,37.9,38.012,39,40.122,44,49,51.9,52 mantêm exatamente os mesmos objetos3D com opacidade positiva e seus valores avaliados, inclusive limites/cortes. PNGs originais vscondition em0,5/14/39s têm maxRGBA0 e nenhum componente diferente; vistos em resolução completa. Render e bench strict não registram errors/unsupported. Os PNGs apoiam a equivalência estática; não houve playback/escuta e não foi comparada a sequência completa codificada do contorno na RTX.

Limites: em t=24..51,9 a colônia tem cerca de3600 objetos3D positivos, portanto condition preserva essa carga. A otimização comprovada é o custo dos invisíveis, principalmente na abertura; não promete ganho de30x em FPS do filme inteiro. GPUwait0 nos logs significa ausência de bloqueio nessa etapa, não inexistência de trabalho de rasterização. Não há segunda medição local: UID55 corrigiu o relato anterior, restartlocal ficouqueued/cancelado. O encode longo já autorizado e iniciado pelo produtor no servidor3 é independente; não o interrompi e não recomendo reiniciar um corte em andamento com fonte diferente.

Próximo passo: arte aceita os quadros equivalentes, produtor decide integração em uma nova versão fora do encode vigente e valida o resultado codificado; recursos mede taxa e agenda se necessário. Até lá, conservar cena original e encode longo autorizado. Futuro fix de motor: calcular a pertença aos blocos3D uma vez por FrameGraph ou rejeitar/filtrar zeros antes de repetir scans, com regressões de transparência, sombras, motion blur e transições. Proposta somente; nenhum código foi implementado.

Reprodução: scripts initial_cpu.py,compare_cpu.py,condition_cpu.py; full.scene.xml,pruned.scene.xml e condition.scene.xml; source.json assets/checksums. Full logs e DIAGNOSIS.json com as provas nesta pasta. Bench: `scene-render-premium render <variante>.scene.xml --frames 15..21 --bench --stats --strict --quality final`. Stills: `render --time 0.5 -o ... --stats --strict --quality final`, sempre servidor2 via sr-remote do próprio ENGINE-ATLAS.
