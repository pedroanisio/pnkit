# Prompt-base de roteiro do canal

Derivado do prompt do dono para "The Tale of Machine Intelligence" (`REFERENCIA-tale-of-machine-intelligence.md`). A estrutura e a redação são dele; os campos entre chaves mudam a cada filme. O que foi acrescentado está marcado com ▸. Versão 1, 2026-10-02.

---

Faça uma pesquisa detalhada e escreva um roteiro completo para um {documentário explainer | curta vertical} do meu canal no YouTube, com o título **“{título}”**.

{O recorte, em duas ou três frases: o que o filme reconstrói ou explica, de onde até onde, e que antecedentes entram quando forem necessários para compreender a história.}

Use como referência narrativa {o canal ou filme de referência e o que se quer dele, por exemplo: History of the Universe: profundidade acessível, senso de descoberta, perguntas que conduzem a investigação e alternância entre grandes transformações e histórias humanas}. Desenvolva uma voz original, sem copiar frases, metáforas ou estruturas específicas.

**A pergunta central é: {uma pergunta, que o filme responde no fim}**

Construa uma história com relações claras de causa e consequência. Conecte as ideias, os obstáculos, as descobertas e as condições materiais que tornaram cada avanço possível: {os fios que o filme tem de ligar}. Selecione os marcos pela importância para a narrativa, evitando uma enumeração de datas, produtos e personalidades.

▸ O canal é da família de 3Blue1Brown, Primer, Branch Education, Animagraffs, Kurzgesagt e Neo. Tudo tem de ser bem explicado, interessante, visual, agradável de ver e agradável de ouvir. Quem fala é uma pessoa que explica com prazer uma coisa difícil e bonita; máquinas, moléculas e contas aparecem como coisas que pessoas constroem, medem e usam.

**Pesquisa e rigor**

- Priorize artigos originais, arquivos históricos, universidades, museus e documentação técnica oficial. Registre fontes e datas para as principais afirmações. {Pesquisa já feita, se houver: caminho.}
- Verifique o estado atual do assunto na data da pesquisa. Diferencie fatos estabelecidos, interpretações, controvérsias e previsões.
- {Os mitos e as simplificações deste assunto que o filme evita.}
- ▸ Diga cada ressalva uma vez, no ponto em que ela muda o que o espectador entende, e siga em frente confiando nele.

**Roteiro e experiência audiovisual**

- {Duração: proponha uma duração adequada à profundidade do tema e justifique-a brevemente | o roteiro deverá embasar um vídeo de X a Y}. ▸ Calcule o tempo de fala a 2,9 palavras por segundo, o ritmo medido da narração do canal, mais as pausas.
- Abra com uma cena ou pergunta intrigante que estabeleça a promessa do vídeo. Desenvolva {capítulos | momentos} conectados, com progressão, mudanças de escala, momentos de surpresa e espaço para reflexão.
- Explique os conceitos para um público curioso, sem formação técnica, usando exemplos concretos e analogias que preservem a precisão.
- Para cada sequência, inclua duração estimada, narração completa, ação visual, animações explicativas, textos essenciais na tela e direção de áudio.
- Planeje imagens que demonstrem mecanismos e transformações: {o que o espectador tem de ver acontecer}.
- Considere que o vídeo será produzido com minha engine **rs-scene-render**. Consulte os recursos disponíveis no repositório https://github.com/pedroanisio/rs-scene-render ▸ (cópia local em `~/src/rs-scene-render`; exemplos em `~/videos/ENGINE-ATLAS/`) antes de propor a execução. Identifique o que pode ser procedural e o que exige assets externos, sem presumir recursos não verificados.
- Encerre respondendo à pergunta inicial e apresentando as questões que permanecem abertas, sem previsões tratadas como certezas.

Entregue uma breve síntese da pesquisa, o conceito narrativo, a estrutura de {capítulos | momentos}, o roteiro audiovisual completo e as referências vinculadas às afirmações relevantes. O resultado deve funcionar como uma história envolvente e autocontida, pronta para orientar a produção.

▸ Entregue em arquivos, na pasta do filme: a narração sozinha, só o texto falado, em inglês (`narration-en-us.txt`); o roteiro de produção cena a cena (`production-script.json`: narração, ação visual, texto na tela, áudio, execução no motor, fontes de cada afirmação, tempos); e os números das demonstrações calculados e conferíveis (`demonstracoes-verificadas.json`).
