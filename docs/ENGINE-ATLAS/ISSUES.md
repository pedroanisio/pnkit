# Limites e achados — engine-atlas-001

cx-engine, binário premium f4b4b95bf192. Nenhuma alteração do motor ou de build.

| ID | Estado | Evidência e consequência |
|---|---|---|
| DOC-01 | Documentação corrigida | Guia §6/§8 Maps agora descreve geo/map e map/globe nativos; §14 trata textStyle como corrigido em 92a007b; Appendix restringe collision avoidance aos labels de basemap. Autorizado na DECISION improve-001, sem alterações do motor. |
| LIMIT-01 | Documentado | DOF é para object3D. Texto e placas threeD continuam nítidos. O exemplo 03 usa f/0.7 para tornar a troca de foco visível; comece em f/1.4–2 num filme. |
| LIMIT-02 | Documentado | 2.5D ordena apenas irmãos threeD consecutivos; não atravessa grupos. Exemplo 04 mantém os recortes consecutivos. |
| LIMIT-03 | Documentado | SSR depende do que está na tela. Sem reflexos de geometria fora do quadro; não substitui uma HDRI ou reflexão física. |
| LIMIT-04 | Documentado | Path tracer: sem cáusticas, vidro opaco aos raios de sombra. Still 05 a 64 samples levou 51.357 s no servidor 2; usar para quadro-herói, não escolher para uma sequência longa sem medir. |
| LIMIT-05 | Documentado | Materiais papel e tecido demonstram roughness/textura/sheen sobre esferas. Isso não reproduz a estrutura de fibras nem o movimento de um pano. |
| QA-01 | Avaliação perceptiva pendente | Stills e frames decodificados podem ser inspecionados aqui. Movimento em playback e escuta dos exemplos com áudio devem ser avaliados pela arte/som; nenhuma nota premium inventada. |

Erros de autoria corrigidos durante preparação: posição de colorManagement na sequência XSD; materials vazio. Não são defeitos do motor.

## ENGINE-01 — falso contato em plano rasante: reproduzido

O A/B muda **somente** `sun.contactShadows`, usando uma cópia do looktest de S12. Não editei o projeto original. Fonte/checksum em `work/contact-shadow-repro/source.json`; cenas full-on/off e minimal-on/off, logs strict, PNGs e `COMPARISON.jpg` na mesma pasta.

No servidor 2, Vulkan/llvmpipe, premium f4b4b95bf192, t=0: região `(220,800)-(850,1200)` da imagem completa cai de **34.40 → 22.49** de luma média codificada. Não é o plano inteiro: a região próxima `(220,1250)-(850,1440)` e o céu de controle não mudam. O mínimo com apenas câmera + plano cinza também cai de **125.55 → 99.59** na região intermediária, sem objeto que pudesse fazer aquela sombra. `metrics.json` traz caixas e diferenças.

Contorno verificado: **`contactShadows="false"` na luz sun** mantém `castShadow="true"` e as sombras de shadow map no cenário completo. Desligue contato por luz em chão extenso com câmera rasante; não compense elevando exposição/ambient, pois só mascara o defeito.

Diagnóstico limitado: o mínimo confirma falsa oclusão do próprio plano no teste em screen space. A implementação atual marcha 16 amostras com espessura `max(len*0.35,2)` e margem fixa de 0.5 (`three.wgsl`, `contact_shadow`). A causa numérica exata e a comparação RTX não foram estabelecidas; nenhum código foi alterado.

## Revisão de vitrine — fonte: REVIEW UID21/24/32 e renders da sessão cx-engine, 2026-10-02

26-r3 aprovado pela arte como rotaA, still3dfaae041e73a05279afee40cd73ea41c1d41cb444cd398c67f6ffc8304a19ce; opcionais não bloqueiam. 01/02/08 trazem A-B nativos em COMPARISON.jpg. Retângulo antigo06 reproduzido: nó behindGlass autoral removido isoladamente em work/glass-rectangle-repro; não é defeito demonstrado do motor. 05 ampulheta128/denoise ainda tem pontos escuros/fireflies isolados; custo166.199s servidor2; vitrine desta primeira leva aguarda revisão, sem score inventado. 06 água interna é geometria presente, mas nível pouco perceptível na refração raster; não usar como demonstração de dinâmica da água.

## ENGINE-02 — S25: opacidade zero custa planejamento, não draw GPU

Diagnóstico solicitado UID54, cx-engine. Cena/pin/provenance em [source.json](work/s25-repro/source.json), [relatório](work/s25-repro/REPORT.md), [DIAGNOSIS.json](work/s25-repro/DIAGNOSIS.json) e [prova condition](work/s25-repro/condition-proof.json). Não foi alterado motor/filme.

Abertura t=0,5:3921object3D no FrameGraph,3872zeros,49meshes desenhadas e2317104triângulos. Remover apenas zeros mantém pixels/draws/triângulos; CPUplanning/submission239,499→7,365ms. Portanto culling para a GPU funciona, mas a enumeração repetida de blocos/irmãos custa CPU antes desse culling. `instances` gera um nó por cópia; não é uma drawcall única.

Contorno testado: adicionar condition por janela/expressão de opacidade, mantendo animações/bloco3D/quantidade. Cópia [condition.scene.xml](work/s25-repro/condition.scene.xml), lista [conditions.json](work/s25-repro/conditions.json). CPUplanning7,972ms; grafos visíveis idênticos em20tempos, PNGs0,5/14/39s com maxRGBA0. Arte e produtor devem aceitar/integrar e verificar nova versão codificada; não foi aplicado ao filme nem ao encode longo atual. O ganho é principalmente enquanto a colônia está invisível;3600objetos ativos ainda custam. Fonte sugere scans quadráticos em three_members; nenhum perfil NVIDIA nem FPSRTX do contorno foi medido. UID55: só servidor3medido, localqueued/cancelado.

Aceites registrados 2026-10-02 16:10:23 UTC: coordinator DECISION UID59 aceita o diagnóstico ENGINE-02 e inclui a proposta no candidato pós-lote; REVIEW UID60 cl-art aceita igualdade dos PNGs0,5/14/39s. Para integrar condition no filme, o produtor entrega janelas a15fps em cada borda de fade, diff0 ou diferença de codificação<=2 de luma média contra o corte vigente. S25 segue NOT READY na arte pelo rótulo THE EARTH, atribuído ao produtor/arte. Nenhum aceite de nova sequência codificada ou autorização para mudar motor/pin foi emitido. Proposta [engine02-candidate.md](/home/pals/.local/share/scene-render/rs-scene-render/maint/engine02-candidate.md).
