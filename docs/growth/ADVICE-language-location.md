# Parecer: idioma e localização do canal (pergunta 4 do dono)

Escrito por cl-growth (pals-growth), 2026-10-02. Todas as páginas foram acessadas em **2026-10-02**. **Isto não é aconselhamento jurídico nem contábil.** Onde o texto diz "consulte contador", a decisão tem consequência de imposto e deve ser confirmada por um contador que conheça a tributação de rendimentos do exterior no Brasil e, se for o caso, nos EUA.

Legenda de confiança: **[F]** fato documentado em página oficial (com link); **[P]** prática de mercado sem fonte oficial que consegui abrir; **[N]** não consegui confirmar.

## Resposta curta

1. **O país do dono não impede a monetização nem muda a receita por view.** O Programa de Parcerias do YouTube (YPP) está disponível no Brasil [F]. A receita por view depende sobretudo de **onde mora o espectador** e do que os anunciantes pagam, não do país do criador [F, em termos gerais; a página não faz a comparação direta "país do criador" x "receita", ver 1a].
2. **O que o Brasil muda é o imposto**, não a elegibilidade: o Brasil **não aparece** na lista de países com tratado de renda com os EUA do IRS [F]. A retenção americana só incide sobre a parte da receita vinda de espectadores dos EUA, a uma taxa de 0 a 30%, e sem tratado a regra geral é o teto [F para a faixa; o "30% sem tratado" é a regra geral do código americano, que não abri nesta sessão: **[N]** na página do IRS].
3. **O canal ainda nem está perto de monetizar**: 41 inscritos (relatório). A porta de entrada com anúncios é 1.000 inscritos e 4.000 horas, ou 10 milhões de views de Shorts em 90 dias [F]. A decisão de localização é real, mas ainda sem urgência: dá tempo de decidir com contador antes da primeira receita.
4. **Não recomendo o segundo canal "nos EUA pelo enteado" como forma de pagar menos imposto**: contas do AdSense não são transferíveis e os formulários de imposto exigem o **proprietário beneficiário** da renda [F]. Só existe uma versão legítima (o enteado é de fato o dono e recebe o dinheiro como renda dele) e ela tem custos e riscos próprios (item 1c).
5. **Rota recomendada hoje: (A), um canal em inglês, o atual.** Razões no item 1d.

---

## 1a. O país do canal ou da conta muda elegibilidade ao YPP, RPM ou alcance?

**Elegibilidade [F].** Para entrar no YPP é preciso "viver em um país/região onde o YPP esteja disponível" ([Requisitos do YPP](https://support.google.com/youtube/answer/72851), acessado 2026-10-02). A lista de países da versão ampliada do programa inclui **Brasil** e **Estados Unidos** ([Visão geral do YPP ampliado](https://support.google.com/youtube/answer/13429240) e [disponibilidade](https://support.google.com/youtube/answer/7101720), acessados 2026-10-02; a lista de países veio de resultado de busca na página da ajuda, não a li linha a linha na própria página: **[N]** se a lista tiver mudado). Portanto o dono, residente no Brasil, é elegível quanto ao país.

Outros requisitos da mesma página [F]: sem avisos de diretrizes ativos, verificação em duas etapas, recursos avançados, uma conta AdSense vinculada.

**Limiares [F]** ([YPP ampliado](https://support.google.com/youtube/answer/13429240)):
- Nível de entrada (500 inscritos, 3 envios públicos em 90 dias, 3.000 horas em 12 meses ou 3 milhões de views de Shorts em 90 dias): abre assinaturas pagas, Super Chat, Super Thanks e compras, **sem receita de anúncios**.
- Receita de anúncios e do Premium: 1.000 inscritos e 4.000 horas em 12 meses, ou 1.000 inscritos e 10 milhões de views de Shorts em 90 dias.
- O canal tem 41 inscritos (relatório de 2026-10-02). Falta cerca de 96% do caminho em inscritos. Os números de views de Shorts e de horas de exibição do canal estão em `ANALYTICS-2026-10-02.md`; nenhum deles chega perto dos limiares, mas não calculei as "horas qualificadas" porque o export não as traz.

**RPM [F, em termos gerais].** A ajuda do YouTube diz que anunciantes escolhem as geografias que querem alcançar e que "diferentes locais têm níveis diferentes de concorrência no mercado de anúncios, então o CPM varia por geografia"; e que a receita depende de fatores como geografia do espectador, se viu um anúncio recentemente e se tem Premium ([Entender a análise de receita de anúncios](https://support.google.com/youtube/answer/9314357), via resultados da busca, acessada 2026-10-02). Ou seja: o que determina a receita é **o país do espectador**, mais tema e demanda de anunciantes. Não encontrei página oficial que diga que o **país do criador** altera o RPM; também não encontrei uma que diga que não altera. **[N]** para essa comparação exata. O que o dono pode fazer é olhar no Studio a receita por país do espectador quando monetizar.

**Idioma e tema [P/N].** A ajuda diz que o idioma do anúncio é direcionado pelo idioma do usuário, localização e histórico ([mesma página](https://support.google.com/youtube/answer/9314357)). Que "inglês rende mais que português" é prática comum de mercado, mas é consequência da mistura de países de quem assiste, não de uma regra do YouTube; **[P]**, sem fonte oficial.

**Alcance [N].** Não achei documentação do YouTube que diga que o país do canal limita o alcance. O sistema de recomendação trabalha com o histórico de cada espectador. Um fato do próprio canal: **35% das views do export vêm do Brasil e 24% dos EUA** (`countries.csv`; ver `ANALYTICS-2026-10-02.md`), com filmes quase todos em inglês e três títulos de destaque em português. O país do dono, portanto, não impediu o alcance nos dois países.

**Configuração do canal [F].** O país do canal fica em Studio > Configurações > Canal > Informações básicas. Não encontrei uma página que o ligue à conta de pagamento. **[N]** o efeito exato.

## 1b. Impostos dos EUA para criador brasileiro

**Todos os criadores monetizados, em qualquer país, precisam informar dados fiscais** ([Requisitos fiscais dos EUA para ganhos no YouTube](https://support.google.com/youtube/answer/10391362), acessado 2026-10-02) [F]:
- "Só a parte dos seus ganhos vinda de espectadores dos Estados Unidos estará sujeita à retenção."
- Para criadores fora dos EUA, com documentação, a retenção é de **0 a 30%** sobre os ganhos dos espectadores americanos, conforme haja tratado.
- Sem informação fiscal até **10 de dezembro**, o Google "pode ser obrigado a reter até 24% dos ganhos totais no mundo".
- "Sua legislação tributária local ainda pode se aplicar aos ganhos do YouTube."
- Formulário W-8BEN (pessoa física fora dos EUA) ou W-8BEN-E (entidade): exigidos do **proprietário beneficiário** da renda, e podem ser usados para reivindicar benefício de tratado (resultados da busca nas páginas [10390801](https://support.google.com/youtube/answer/10390801) e [10391362](https://support.google.com/youtube/answer/10391362)); o pagamento do YPP é tratado como **royalties** (mesma fonte).
- A ajuda manda confirmar com um assessor tributário se há direito a benefício de tratado.

**Tratado Brasil-EUA [F].** Brasil **não** consta na [página "United States income tax treaties – A to Z" do IRS](https://www.irs.gov/businesses/international-businesses/united-states-income-tax-treaties-a-to-z) (a lista de B vai de Bangladesh a Bulgária sem Brasil), nem nas tabelas do IRS (Tabela 2, PDF "tax-treaty-table-2", em que a seção de "B" tem Bangladesh, Barbados, Bélgica e Bulgária e nenhuma linha do Brasil), acessadas 2026-10-02. O que o Brasil tem com os EUA são acordos de troca de informação e FATCA, não tratado de renda (resultado de busca no IRS, **[P]** na interpretação; o texto desses acordos não foi lido).

**Consequência provável [P/N]:** sem tratado, o benefício de taxa reduzida não existe e a retenção sobre a parte americana tende ao teto de 30%. A faixa "0–30%" é da ajuda do YouTube [F]; "o teto vale quando não há tratado" é a regra geral do código americano, **[N]** nesta sessão, e deve ser confirmada pelo contador. Em termos de volume: espectadores dos EUA são 24% das views do export, então a retenção, se for 30%, recairia sobre **a parte da receita vinda dessa fatia** (valor depende do RPM americano, que não conheço: **[N]**).

**O lado brasileiro [F, com ressalva].** A Receita Federal diz que rendimentos recebidos do exterior por pessoa física residente no Brasil estão sujeitos ao **carnê-leão** (recolhimento mensal) e à declaração anual, que o valor se converte em dólar e depois em reais pelas regras da Receita, e que o imposto pago no exterior só pode ser compensado quando há tratado ou reciprocidade ([Carnê-Leão, Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/carne-leao), via resultados da busca, acessada 2026-10-02). Se o 30% retido nos EUA pode ser compensado no Brasil sem tratado e como (reciprocidade, limite legal): **[N]**. Também **[N]** como a Receita classifica o pagamento do YouTube (royalties, serviços ou outro código) e se convém abrir CNPJ (MEI ou outro regime). **Esse é o ponto em que o dono deve consultar um contador antes de monetizar.**

**O que muda com conta nos EUA [F/N].** Um criador que reside nos EUA entrega o formulário de tratamento de residentes (W-9) e não sofre a retenção para não residentes; o ganho vira renda americana dele. A ajuda diz que o limite máximo sem informação válida é 24% ([10391362](https://support.google.com/youtube/answer/10391362)). Que isso resulte em "imposto menor" **para o dono** depende de quem é o titular, ver 1c.

## 1c. Segundo canal "localizado nos EUA" pelo enteado

O que a documentação diz:

- **Uma conta AdSense por nome de beneficiário** ("só é possível ter uma conta do AdSense ou AdSense para YouTube sob o mesmo nome de beneficiário"); duplicidade leva à desaprovação e à desativação da monetização ([Configurar uma conta AdSense para YouTube](https://support.google.com/youtube/answer/9914702), acessada 2026-10-02) [F].
- **Contas AdSense não são transferíveis**: os termos não permitem transferir a titularidade; só dá para corrigir nome ou endereço por erro de grafia, casamento, óbito, fusão (página [Alterar nome e endereço do perfil de pagamentos](https://support.google.com/adsense/answer/160202), via busca) [F]. O **país do endereço de pagamento não pode ser mudado**: seria preciso fechar a conta e abrir outra ([Alterar país](https://support.google.com/adsense/answer/2628816), via busca) [F].
- O formulário fiscal (W-8BEN) pede o nome do **proprietário beneficiário** da renda (W-8BEN) [F]; o nome legal do formulário deve bater com o do perfil de pagamentos (busca, mesma família de páginas) [F].
- Política de monetização: com a monetização suspensa, não se deve criar canais novos para contornar a restrição, "isso pode levar ao encerramento de todos os canais" ([Políticas de monetização](https://support.google.com/youtube/answer/1311392), acessada 2026-10-02) [F]. Esse trecho é sobre suspensão; não se aplica ao caso, só mostra que o YouTube olha canais relacionados.
- O YouTube também diz que não permite conteúdo "em massa, genérico, repetitivo" (conteúdo inautêntico) ([mesma política](https://support.google.com/youtube/answer/1311392)) [F]: dois canais com o mesmo material em dois idiomas, ou com filmes repetidos, precisam ser trabalho original em cada um.
- A transferência da **propriedade do canal** entre contas é possível por Conta de Marca ([Alterar proprietários de canal](https://support.google.com/youtube/answer/4628007)) [F], mas isso não transfere a conta AdSense.

Em linguagem direta: **a renda pertence a quem é o beneficiário no cadastro de pagamento e no formulário fiscal.** Dá para ver duas versões:

1. **O enteado é de fato o dono e operador do canal** (conta e AdSense em nome dele, canal criado por ele, o dinheiro dele). Isso é permitido pelas regras acima. Consequências: ele paga os impostos dos EUA que lhe couberem; o canal deixa de ser do dono; qualquer dinheiro que passe dele para o dono tem tratamento próprio (doação ou pagamento por serviço) no Brasil e nos EUA: **[N]**, consultar contador nos dois países. O dono perde controle de monetização e o histórico dos filmes atuais não vai junto (item 1d).
2. **O enteado é só o nome na conta enquanto o dono produz e fica com o dinheiro.** Isso afirma, em formulário assinado, uma titularidade que não corresponde à realidade. Não conseguiria recomendar, e pode contrariar os termos do AdSense e as regras fiscais dos dois países. **[N]** o enquadramento legal exato: ponto para contador/advogado, não para este parecer.

Eu não recomendo a segunda e só sigo adiante com a primeira se o dono quiser **transferir de fato** a atividade. Como o canal ainda não monetiza, nada disso exige decisão imediata.

## 1d. Três rotas

| | (A) Um canal, em inglês (hoje) | (B) Canal atual vira português; novo canal em inglês | (C) Canal atual em inglês; novo canal em português, outros temas (humor) |
|---|---|---|---|
| O que acontece com os 41 inscritos e o histórico | Mantém tudo. | Os 41 inscritos e as views antigas (Lone Crab, vgpu, filmes de 2026-09) ficam num canal que passa a ser em português; o canal novo recomeça do zero. O YouTube não move inscritos entre canais [N, não vi página; é a prática conhecida]. | O canal atual segue. O novo recomeça do zero, com público e linguagem diferentes. |
| Custo de produção | Nenhum a mais. | Alto: todos os filmes futuros em inglês iriam para um canal sem inscritos; refazer o pacote (nome, banner, playlists). | Um segundo canal inteiro: pauta, estilo, trilha, e o dono já não consegue produzir ao ritmo desejado (30/dia) no primeiro. |
| Encaixe com o que o canal tem | Os filmes têm **texto em inglês na tela**. Em contrapartida, os dois Shorts em português do export estão entre os de maior retenção (80% e 74%); é observação de dois casos, não conclusão sobre idioma. | Brasil é 35% das views, mas isso vem de Shorts, e ainda não sei se vem de vídeos em português (o export não liga país a vídeo). | Humor é outro público e outra marca; a mistura "ciência explicada + humor" no mesmo canal não é recomendada pelo YouTube, que sugere canais separados para idiomas diferentes (ver abaixo). |
| Risco de política | Nenhum específico. | Nenhum específico. | Dois canais com conteúdo reaproveitado entrariam em "conteúdo inautêntico/em massa" [F]; filmes diferentes, não. |
| Monetização | Uma conta AdSense, uma retenção dos EUA de até 30% sobre a parte americana [F/P]. | Mesma conta (pessoa física) dá para os dois canais? Um AdSense por beneficiário [F]; **dois canais do mesmo dono podem ligar ao mesmo AdSense**: **[N]**, não li essa página. | Idem. |

O YouTube descreve as estratégias de **canal único**, **canais separados por idioma** (útil para alfabetos ou termos de busca diferentes) e **híbrido** ([Estratégia para audiências globais](https://support.google.com/youtube/answer/6070467), acessada 2026-10-02) [F]. Não diz qual rende mais. Quanto à faixa "áudio em português nos filmes em inglês", a ajuda de áudio multilíngue exige recursos avançados, que o canal tem (resposta 1 do dono); o dono decidiu **manter a dublagem automática desligada**, então essa rota seria só com faixas feitas à mão, e o canal não tem nenhuma hoje.

**Recomendação (prática, não regra): rota (A) agora.**
1. O canal tem tração em inglês e português ao mesmo tempo sem separar nada, e a separação teria custo certo (perder histórico e começar do zero) contra um ganho que ninguém demonstrou.
2. Nada na conta de pagamento muda o RPM, e a monetização está longe (41 de 1.000 inscritos).
3. Se o dono quiser humor em português, a rota (C) é um **projeto novo**, com custos de produção e de marca próprios, a decidir por razão editorial e não fiscal.
4. Reavaliar quando existirem dados que hoje faltam: país do espectador por filme, idioma do público, receita por país depois da monetização.

## 2. O que fazer, em ordem

1. Nada a mudar no YouTube agora por causa do país. Continuar rota (A).
2. **Antes de monetizar** (ou ao se aproximar de 1.000 inscritos): consultar um contador que conheça (i) carnê-leão/IRPF para rendimentos do exterior, (ii) se há como compensar a retenção dos EUA, (iii) se compensa abrir CNPJ.
3. No dia do cadastro AdSense: entregar o **W-8BEN** (pessoa física) até **10 de dezembro** do ano em curso, para evitar a retenção máxima mundial de 24% [F]; o contador diz se há benefício a reivindicar.
4. Se o dono quiser seguir a ideia do segundo canal, conversar primeiro com contador no Brasil **e** nos EUA; decidir **titularidade real** antes de abrir qualquer conta.

## 3. O que não consegui confirmar

- A lista exata de países do YPP na própria página (li o resumo da página e resultado de busca).
- Se o país do criador altera RPM ou alcance (sem página oficial).
- Taxa exata aplicada hoje a um criador brasileiro (sem tratado) e o tratamento da compensação no Brasil.
- Como a Receita classifica o pagamento do YouTube e se um CNPJ muda o resultado.
- Se dois canais do mesmo titular podem ligar à mesma conta AdSense (a página só diz uma conta por nome de beneficiário).
- Que inscritos não migram entre canais (prática conhecida, sem página lida).
- Todas as páginas foram lidas por ferramenta de extração de texto (WebFetch e resultados de WebSearch); onde digo "via busca" o texto vem do resumo do resultado, não da página lida por inteiro. Antes de qualquer decisão financeira, conferir a página original.
