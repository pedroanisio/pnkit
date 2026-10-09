# 27 — Quebras sob controle

Demonstração técnica de `engine-linebreaks-001`, código-fonte em teste. O binário premium fixado continua inalterado e ainda não aceita `lineBreaks="source"`. Este exemplo é um apêndice de desenvolvimento; os recursos 01–26 usam o pin vigente.

[Still nativo](still.png) · [clipe 3,5 s](clip.mp4) · [amostras do clipe](MOTION-SAMPLES.jpg) · [XML opt-in](scene.xml) · [controle sem atributo](legacy.scene.xml) · [evidência de testes/pixels](evidence.json) · [checagem do vídeo](clip-check.json).

A mesma cue `Uma ideia&#10;por linha` aparece com o preset highlight duas vezes: o padrão greedy forma uma linha; source encerra a primeira linha depois de “ideia”. A palavra ativa mantém o mesmo instante e índice nas duas apresentações. O still é o quadro 42, t=1,75s, 1080×1920. A fonte é Archivo do kit de marca, com licença em ../assets/Archivo-OFL.txt.

```xml
<captionTrack id="cc" language="pt" lineBreaks="source"
              maxCharsPerLine="80" maxWordsPerLine="6" maxLines="2">
  <cue start="0" end="3.5" text="Uma ideia&#10;por linha"/>
</captionTrack>
```

Cada newline encerra a linha atual; os limites de palavras/caracteres continuam quebrando linhas longas, e maxLines continua dividindo páginas. Linhas vazias não criam linhas de legenda vazias. Uma palavra individual maior que maxCharsPerLine continua indivisível, como no comportamento anterior. One-word mantém uma palavra por página. Em source, spans com várias palavras são divididos pelo comprimento; tempos de palavras individuais e ênfase são preservados. Novas linhas não são palavras artificiais. O filtro de palavrões e cortes/remarcações reversas preservam a divisão em linhas.

Os 84 quadros foram renderizados no servidor2 por um harness Cargo test usando diretamente sr-model/sr-eval/sr-gpu da árvore alterada; cada quadro exige stats.errors e stats.unsupported vazios. Não foi compilado um executável candidato scene-render. O vídeo foi codificado desses PNGs com h264_nvenc, por um único sr-gpu curto. O log registra84 quadros em 0,51s, speed6,58x; ffmpeg não calcula fps em jobs menores que1s. A taxa derivada é cerca de 165 quadros/s; a renderização nativa separada levou 45,218s para 84 quadros e um controle. Custos de compilação não fazem parte dessas taxas.

Controle: legacy.scene.xml renderizado pela biblioteca alterada e pelo premium fixado em t=1,75s produziu diferença RGBA máxima0, nenhum componente diferente. Além disso, os testes de pixels com classic/highlight/karaoke/one-word, em 0,25/1,75/3,25s, confirmam que default=greedy explícito=newlines substituídos por espaços. Source muda as quebras nos três primeiros presets e preserva one-word.

Usos: duas linhas com frase em ordem deliberada; nomes/qualificadores em linhas separadas; gráficos explicativos que precisam manter a palavra ativa numa posição planejada. Ainda depende de integração e decisão de build/rollout. Stills e amostras codificadas foram examinados; não houve escuta ou avaliação de playback, e isto não é um corte com aprovação de publicação.

Reprodução, patch e logs: `/home/pals/.local/share/scene-render/rs-scene-render/maint/engine-linebreaks-001/REPORT.md`. Não copie este atributo para um filme que usa o binário fixado atual.
