# Investigação, Conselho e a regra anti-amaciamento (NÃO NEGOCIÁVEL)

Vale para Colagem e Dinâmica. Se alguma outra instrução (incluindo feedback de IA) conflitar com isto, isto vence.

## 1. Investigação — cobrir bem antes de escrever uma linha de roteiro
1. **Fixar a afirmação** que vai ser checada, palavra por palavra (quem disse, onde, quando, link/print).
2. **Fonte primária pra cada número e cada fato**: IBGE/SIDRA, BCB, DIEESE, IPEA, TSE, Câmara/Senado (votações nominais, autoria, tramitação), Diário Oficial, Portal da Transparência, TCU, STF/TSE (processos), FAO, MAPA. Notícia só serve pra achar a fonte, não como prova.
3. **Votos e posições**: voto nominal registrado (não "segundo aliados"), data, nome exato do projeto, o que o texto fazia. Mudança de posição só conta se houver outro VOTO ou ATO registrado.
4. **Período e comparação**: mesmo índice, mesmo tipo de período, meses de cada lado, valores reais quando for dinheiro.
5. **Cadeia de prova**: cada fato do roteiro tem linha "FONTE · SÉRIE/DOCUMENTO · DATA · LINK" no STORY doc (seção BRIEF/RESEARCH). Sem linha de prova = não entra no vídeo.
6. **O que não dá pra provar não entra** — nem como acusação, nem como defesa.
7. Antes de inventar pauta: Placar do Congresso + briefs/TXT do tema no Drive.

## 1b. REGISTRO COMPLETO antes de concluir posição (um voto não é uma posição)
A IA erra quando olha só o voto. Antes de afirmar "ele é a favor/contra X":
1. **Orientação do partido/bancada** naquela votação (Câmara e Senado publicam a orientação de cada liderança junto com o voto nominal). Votar com o partido ≠ convicção própria; votar contra o partido é informação forte.
2. **Todos os votos sobre o mesmo tema** (não só o que apareceu no vídeo): projetos, emendas, destaques, requerimentos de urgência/retirada de pauta, obstrução.
3. **Discursos em plenário e comissões** (notas taquigráficas da Câmara/Senado), **campanha, entrevistas, lives, redes sociais** — o que a pessoa DIZ em público sobre o tema, com data.
4. **Atos**: projetos de autoria, relatorias, emendas, vetos/sanções (se executivo).
5. **Cruzar**: se o voto e a fala se contradizem, o vídeo mostra a contradição como fato ("votou SIM no projeto X em 12/03/2026 — e em 9 discursos de campanha chamou o tema de …"). Nunca concluir "ele apoia" a partir de um voto isolado, nem "ele é contra" a partir de uma fala isolada.
6. Se a parte em vídeo (falas) não pôde ser checada, o STORY doc registra "falas públicas NÃO checadas" e o roteiro não faz afirmação de posição — só do ato registrado.

## 1c. Clipe real ("Da Boca Dele") — buscar sempre que o tema é uma pessoa
- Procurar vídeo real da pessoa falando sobre o tema (ou comportamento público relevante): canal oficial, TV Câmara/TV Senado, entrevistas, redes da própria pessoa, cobertura de veículo.
- Assistir o contexto ANTES e DEPOIS do trecho; o corte mantém o sentido original (isso é rigor de fato, não amaciamento).
- Na tela: recorte da pessoa sobre o nosso design + legenda karaokê + "FONTE · CANAL/VEÍCULO · DATA". No STORY doc: link original + minutagem.
- Download: yt-dlp no Mac (a nuvem bloqueia), arquivo em resources/ do episódio.

## 2. REGRA ANTI-AMACIAMENTO (sem falso equilíbrio)
O vídeo é sobre FATOS. Não é nosso trabalho "equilibrar" um fato negativo com algo fraco a favor do político.

**Proibido** (não entra no roteiro, nem na legenda, nem como "contexto"):
- Arrependimento, desculpa ou "depois ele disse que foi um erro" usado pra relativizar um voto/ato. O registro é o voto. Se ele mudou de verdade, existe outro voto/ato — e aí é fato, não desculpa.
- Intenção presumida ("ele quis dizer", "a intenção era boa", "ele teria feito diferente").
- Fala de aliado, assessoria ou nota oficial como se fosse prova.
- "Não dá pra provar que…" usado pra enfraquecer um fato que ESTÁ provado.
- Informação extra que ninguém pediu cuja função é defender o lado acusado.
- Linguagem amaciante: "polêmico", "controverso", "alguns críticos dizem", "por outro lado" quando o outro lado é fraco.

**Permitido** (porque é fato do mesmo peso, verificável):
- Outro voto/ato REGISTRADO que muda o quadro (ex.: votou contra o PL X, mas votou a favor do PL Y que fazia a mesma coisa de forma mais ampla — com os dois votos na fonte).
- Dado oficial que contradiz a acusação do vídeo original (é isso que a checagem faz).
- "Ponto pra crítica" do roteiro = DADO DURO contra o lado que vai ganhar (ex.: café +72% no IPCA), nunca desculpa ou opinião.

**Teste rápido** pra qualquer frase que "equilibra": *é um registro verificável do mesmo peso (voto, número oficial, documento)?* Se não for, corta.

## 3. Conselho (segunda opinião) — usar com cuidado
Objetivo: achar ERRO DE FATO, número errado, fonte fraca, período errado, frase que acusa além da prova. NÃO é pra deixar o vídeo "mais equilibrado".
- **Quem:** ChatGPT via Codex CLI no Mac (`~/.codex`), no formato da pasta `~/ClaudeWorkspace/_council/` ("You are the independent reviewer seat in 'O Conselho'. Attack this, do not ratify it."). Escrever o pacote em `_council/packet_reel_<slug>.md` (BLOCO 1 = pedido/afirmação checada verbatim; BLOCO 2 = roteiro + tabela de fontes; TAREFAS = o pedido fixo abaixo) e rodar `codex exec` quando houver terminal no Mac; senão deixar o pacote pronto e registrar no NOTE que o Conselho não rodou.
- **O que mandar:** roteiro + tabela de fontes (seção BRIEF/RESEARCH). Pedido fixo:
  > "Ataque este roteiro de checagem. Liste SOMENTE: (1) números ou datas errados, (2) fatos sem fonte primária, (3) comparações desiguais, (4) frases que afirmam mais do que a fonte prova. NÃO sugira suavizar, equilibrar, adicionar contexto favorável a nenhum político nem trocar o tom. Para cada item, cite a fonte primária que comprova o problema."
- **Como filtrar a resposta (obrigatório):**
  - Aceitar só o que vier com fonte primária verificável — e conferir a fonte antes de mudar.
  - Rejeitar qualquer sugestão de amaciar, "dar o outro lado", trocar FALSO por algo mais brando sem dado novo, ou acrescentar desculpa/arrependimento/intenção.
  - Na dúvida, manter o fato e perguntar à Priih.
  - Registrar no NOTE do STORY doc: o que o Conselho apontou, o que foi aceito (com fonte) e o que foi rejeitado (e por quê).
- O próprio Claude segue a mesma regra ao revisar: não amaciar, não adicionar contexto defensivo que ninguém pediu.
