# Analytics do canal: leitura de 2026-10-02

Fonte: `~/_tmp/analytics-2026-10-02.zip` (cards, countries, daily, devices, per_video, retention_top, traffic_sources, viewer_type_shorts) e `~/_tmp/report-pals-2.pdf` (listagem pública, "as of 2026-10-02"). Nenhum outro arquivo foi lido. Todos os números abaixo vêm desses dois arquivos; o que eu calculei está marcado "(cálculo meu)". Quem escreveu: cl-growth, 2026-10-02.

## 1. O que o canal é hoje (fatos dos arquivos)

- 41 inscritos, 64 envios (26 longos, 38 Shorts), 23.082 views somadas nas listagens públicas (report-pals-2.pdf).
- O export de Studio cobre menos views que a listagem: 12.692 views na soma de `daily.csv` e 12.573 em `traffic_sources.csv` (cálculo meu). Não sei por que diferem do relatório público (23.082): pode ser janela de datas, views de Shorts contadas de outro modo ou os números arredondados da listagem. **Não consegui confirmar a causa.** Uso o export para tudo que é taxa e o relatório só para títulos e datas.
- Os dois últimos dias do export (2026-09-28 e 09-29) somam 8.782 views, 69% do total do export (cálculo meu). Antes disso o canal ficava quase sempre abaixo de 100 views por dia; em maio, de 0 a 5. Os picos anteriores (22–26 de agosto, 29–31 de agosto com 229, 292 e 243) vêm do vgpu e de Shorts da época; não tenho a origem exata de cada um.
- Inscritos ganhos no export: 29 em `daily.csv`, 1 perdido; 25 em `per_video.csv`; 41 no relatório. Os três números não batem entre si. A coluna `subscribersGained` de `countries.csv` está zerada em todas as linhas e não serve. **Tratar qualquer "inscritos por filme" abaixo como ordem de grandeza.**
- Os dois dias com mais views (09-28 e 09-29) deram 16 inscritos ganhos (cálculo meu), cerca de 1 inscrito para 550 views, o que é a taxa de um canal que nunca pediu nada.

## 2. Origem do tráfego (`traffic_sources.csv`, 12.573 views)

| Origem | Views | Parcela (cálculo meu) | Minutos assistidos |
|---|---:|---:|---:|
| Shorts (feed) | 7.778 | 62% | 1.183 |
| Vídeo relacionado | 2.123 | 17% | 2.422 |
| Inscritos | 1.161 | 9% | 440 |
| Busca no YouTube | 862 | 7% | 307 |
| URL externa | 194 | 1,5% | 219 |
| Outras (canal, playlist, página de som, etc.) | 455 | 3,6% | |

- Os Shorts trazem 62% das views, mas só 1.183 minutos; "vídeo relacionado" traz 17% das views e **2.422 minutos, o dobro**. Cada view de relacionado vale cerca de 1,14 min; cada view de Shorts, 0,15 min (cálculo meu).
- Só 9% das views vêm de inscritos. Com 41 inscritos, isso é esperado; mostra que ainda não existe base que volte.
- Playlist: 4 views. Canal (página): 103. Hoje ninguém navega pelo canal; entra pelo feed e sai. É a razão de o plano de fim de tela e de playlists importar, e também de ele ter, por enquanto, pouca base para testar.
- **Cartões:** 0 impressões, 0 cliques (`cards.csv`). Nenhum filme tem cartão ainda; é o esperado, não é um resultado.

## 3. Retenção

Todas as curvas vêm de `retention_top.csv` (100 pontos por vídeo; só 8 vídeos). Valores lidos nos pontos 5%, 25%, 50%, 90% e 100% do tempo do vídeo. "Audience watch ratio" acima de 1 no início é a repetição de views (loop de Short), não um erro.

| Vídeo | Tipo | 5% | 25% | 50% | 90% | 100% | Duração média / % média |
|---|---|---:|---:|---:|---:|---:|---|
| Segunda Guerra Mundial explicada (PT) | Short | 1,39 | 0,97 | 0,71 | 0,59 | 0,53 | 24 s / 80,3% |
| Por que a luz demora milhares de anos (PT) | Short | 1,33 | 0,93 | 0,66 | 0,51 | 0,39 | 22 s / 74,1% |
| Iran War in 37 Seconds | Short | 1,35 | 0,87 | 0,62 | 0,47 | 0,35 | 26 s / 70,9% |
| How a Jet Engine Works in 30 Seconds | Short | 1,30 | 0,88 | 0,63 | 0,50 | 0,34 | 22 s / 71,5% |
| This Protein Cage Builds Itself | Short | 1,14 | 0,68 | 0,50 | 0,35 | 0,21 | 17 s / 57,4% |
| Why Does a Bubble Go "Plink"? | Short | 1,10 | 0,52 | 0,31 | 0,21 | 0,14 | 13 s / 43,3% |
| The Lone Crab | Longo | 0,64 | 0,14 | 0,07 | 0,03 | 0,03 | 60 s / 12,8% |
| WebGPU Without the Boilerplate (vgpu) | Longo | 0,62 | 0,38 | 0,19 | 0,10 | 0,09 | 82 s / 22,5% |

Leituras:

- **Entre os Shorts, a retenção de abertura (5%) já está acima de 1,0** em todos: quem fica nos primeiros segundos revê. Os que seguram até o fim são os de 70 a 80% de duração média (Segunda Guerra, Luz do Sol, Iran, Jet Engine). O de "plink" cai a 31% na metade. Isso é consistente com a regra do canal de Shorts com gancho de uso, mas **um conjunto de 6 Shorts não prova a regra**; é pista, não conclusão.
- **Os dois longos que o export mostra perdem a maior parte do público nos primeiros 25%** (Lone Crab 14% em 25%; vgpu 38%). Não são filmes da leva atual (The Lone Crab é de abril, vgpu de agosto), então não dizem nada sobre v028, v019, v024 e v025. **Não há curva de retenção de nenhum filme recente de formato longo no export**, só os dois acima. Não posso dizer se um fim de tela de 15 a 20 s é longo demais ou onde os filmes novos perdem gente.
- `relativeRetentionPerformance` aparece no arquivo (0,07 a 0,55 nos pontos lidos). Não sei a escala exata usada pelo YouTube para essa coluna, então não a interpreto além da ordem entre vídeos.

## 4. Shorts: vistos x pulados

- `viewer_type_shorts.csv`: views de Shorts 8.666 (`creatorContentType = shorts`) e 4.026 em vídeo longo (`videoOnDemand`) (soma 12.692, igual a `daily.csv`). Ou seja, 68% das views do canal são em formato Short (cálculo meu).
- **Não há "viewed vs swiped away" no export.** A taxa de quem escolhe ficar não pode ser calculada. Peço esse número ao dono (Studio > Analytics > um Short > "Viewed vs swiped away").
- Entre os Shorts do relatório público: a mediana de views é 266 e o máximo 1.379 (o "ontem para hoje" pode ter inflado). Os 10 melhores têm de 974 a 1.379 views, todos publicados entre 2026-09-28 e 10-01 (relatório). Isso é uma onda de 4 dias, não um padrão de crescimento.

## 5. País, idioma e aparelho

- Países (`countries.csv`, 7.654 views nos 25 países listados): **Brasil 2.716 (35%)**, EUA 1.835 (24%), Índia 604, Filipinas 477, Indonésia 329, Canadá 284, Alemanha 198, Reino Unido 158, Austrália 157. Brasil e EUA juntos são 59% das views listadas (cálculo meu).
- Minutos assistidos: BR 488, US 395, IN 259, PH 139 (os minutos por view são maiores nos EUA, 0,22, que no Brasil, 0,18, e muito maiores na Índia, 0,43, e no Vietnã, 0,82; cálculo meu, amostras pequenas).
- **Não há coluna de idioma do público nem de idioma do vídeo.** O Brasil lidera em views, e três títulos públicos de destaque estão em português (o Short de Segunda Guerra, o Short da luz do Sol e o longo "Como funciona o Sol?"); não posso separar "público brasileiro" de "vídeos em português". Os dois Shorts em português estão entre os de maior retenção do canal (80% e 74% de duração média). Isso é um sinal, não uma prova de que o público brasileiro é a base: o export não liga país a vídeo.
- Dispositivo (`devices.csv`): celular 9.774 (77%), computador 1.451, tablet 853, TV 483 (cálculo meu). A faixa de fim de tela e os textos na tela precisam funcionar em celular antes de tudo.

## 6. Longos: o que o relatório público diz (26 longos, mediana 30 views, p90 560)

- Mediana de 30 views em longos contra 266 em Shorts (relatório). A distribuição é muito concentrada: The Lone Crab 2.192 views (74× a mediana, abril), vgpu 929, v028 (robô maratona) 619 (2026-09-29), Como funciona o Sol 502 (2026-09-28).
- Curtidas: 2,62% (mediana dos 18 mais novos longos) e 2,38% (38 Shorts). **Comentários: 0,0% em ambos.** Ninguém comenta. Isso é relevante para o comentário fixado: ele não vai atrair resposta sem uma pergunta real, e o plano não deve contar com isso.
- Cadência pública: 16 longos em 30 dias (3,7/semana) e 38 Shorts em 30 dias (8,9/semana) segundo o relatório; em 365 dias, 26 longos e 38 Shorts. Isto é **o ritmo do mês passado, não uma promessa**; a meta de 30 por dia do dono ainda não é realidade e nenhum texto a promete.

**Nota sobre o relatório público:** os 10 longos e os 10 Shorts listados em `report-pals-2.pdf` não incluem nenhum dos filmes da leva atual publicados em 2026-10-02 (v016, v019, v022, v024 a v029): eles ainda não aparecem entre os mais vistos. Não há, portanto, nenhum número de views, retenção ou inscritos para o retrofit que estou propondo; a linha de base é o canal antes dele.

## 7. O que os números dizem e o que não dizem

**Dizem (com os limites acima):**

1. O crescimento recente é de Shorts e de "vídeo relacionado", não de inscritos nem de busca. Quem chega vê e vai embora: 41 inscritos para cerca de 13 mil a 23 mil views.
2. "Vídeo relacionado" tem muito mais tempo assistido por view que o feed de Shorts. A ponte Short para filme longo é o ponto de maior valor por view; o plano já tem o link de vídeo relacionado do Short como pedido principal.
3. Países e dispositivo mostram um público majoritariamente de celular, no Brasil e nos EUA. O fim de tela e a tela de abertura precisam ser lidos em tela pequena.
4. Nenhum cartão existe ainda, e o canal não tem playlists com tráfego.

**Não dizem:**

- Se um pedido de inscrição falado no fim aumenta inscritos: nenhum filme atual tem pedido, e as 8.782 views de dois dias vêm de Shorts e de recomendação.
- Retenção de qualquer filme longo recente; só há os dois mais antigos.
- Idioma do público; viewed vs swiped away; cliques em elementos de fim de tela (ainda não existem); inscritos por filme com confiança.
- Se o Brasil seria o público fiel: ver o parecer de idioma em `ADVICE-language-location.md`, onde o ponto é tratado.

## 8. O que isso muda no plano (resumido; detalhes nos arquivos de plano)

1. O fim de tela e o link "vídeo relacionado" dos Shorts entram na ordem de prioridade antes de qualquer coisa de banner ou trailer: é onde o canal já tem tráfego de maior valor.
2. O comentário fixado pergunta algo concreto e específico ao filme em vez de esperar discussão (comentários: 0%).
3. Não escrever número de retenção ou de inscrição como meta; medir a mudança em duas semanas depois do retrofit comparando o mesmo conjunto de filmes.
4. Pedir ao dono em duas semanas: curva de retenção dos longos recentes (v028, v019, v024, v025), cliques de fim de tela por elemento, "viewed vs swiped away" por Short, e idioma do público (Studio > Público).
5. Não prometer frequência. A cadência recente (3,7 longos e 8,9 Shorts por semana) existe, mas o dono ainda não confirmou o que prometer.
