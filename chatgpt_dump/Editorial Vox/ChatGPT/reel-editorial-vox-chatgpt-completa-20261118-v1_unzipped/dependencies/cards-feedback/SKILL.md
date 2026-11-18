---
name: "cards-feedback"
description: "Cards de antes e depois na prévia do reel, pra ela ver o que mudou e escolher trocar, juntar ou manter."
---

# Cards de feedback (antes e depois na prévia)

Por que existe (pedido dela, 12/nov/2026): quando eu mudo uma cena por conta própria, às vezes mudo outra parte, tiro algo que devia ficar ou esqueço de pôr de volta, e ela não acha o que mudou. Ela também não quer ler propostas longas no chat. A ideia é ela VER o antes e o depois e decidir se troca, junta os dois ou mantém.

Isto não trava a proatividade: o que é óbvio eu corrijo direto, como sempre. Mudança grande (ver "Quando vira card") ganha o par antes e depois na aba, mesmo que eu já tenha aplicado, pra ela poder conferir.

## 0. Mesmo padrão das outras skills (não é skill do zero)
Esta skill é uma camada em cima do ciclo de todo reel. Tudo que vale pra prévia e pra auditoria vale aqui também:
- **Prévia:** padrão mínimo do reel-pasta-roteiro-auditoria (velocidades, pulos de 5/10/30 s, caixa de notas com copiar, download, legenda e 1º comentário, aba do vídeo original). Republicar no MESMO link, guardando a versão anterior.
- **Card proposto passa pelas mesmas conferências da cena de verdade:** zona segura e sobreposição com as fontes reais (reel-zona-segura), legenda em 2 linhas equilibradas, quebras de linha, tamanhos mínimos, maiúscula no começo de bloco, cabeça recortada com chip de ideologia, cor do dia.
- **Conteúdo do card proposto:** fatos com fonte, regras políticas (governo atual + 🦑, de quem é a responsabilidade, peso não empate, exemplo equivalente do outro lado), sementinhas e contexto de todo termo (roteiro-storytelling 8b), fala com cara de conversa (escrita-humana), palavras que derrubam alcance, e a leitura curta da auditoria-dissonancia em conteúdo político.
- **Formato visual:** os labels e o botão de mostrar/esconder seguem o formato dos recados da auditoria-na-tela (etiqueta, fonte 800, ≥ 22 px no palco, escolha lembrada no localStorage com try/catch). Nada disso entra no MP4, na capa nem em print de entrega.
- **Registro:** todo feedback dela entra na LISTA DE FEEDBACK do ROTEIRO (com data, nas palavras dela) e cada troca aprovada vira uma NOTE no ROTEIRO, com o que saiu e o que entrou. A fala aprovada atualiza o roteiro antes da voz final.

## 1. Labels de card (em toda prévia de reel, desde a primeira versão)
- Cada cena ganha um label pequeno "Card 1", "Card 2"... que aparece quando a cena entra e some depois de uns 2 s (não fica fixo).
- O label é só da prévia: sai junto com os recados no botão "Com recados / Sem recados" e NUNCA entra no MP4, na capa nem em print de entrega.
- Quando ela falar "card 3", é essa cena.

## 1b. A página principal é SEMPRE o vídeo (regra dela, 12/nov/2026)
- A primeira aba que abre na prévia é o vídeo tocável da versão nova (player com voz, velocidades, pulos, notas). Nunca abrir a prévia direto na aba de mudanças.
- A aba de mudanças/feedback é secundária: fica ao lado ou embaixo do vídeo, como apoio pra conferir o antes e depois.
- Mesmo quando a rodada só mudou poucas cenas, monta o vídeo inteiro na aba principal (com voz grátis) e deixa os cards de mudança como segunda aba.

## 2. Aba Feedback (vem em toda prévia, vazia no começo)
- Abaixo da prévia (ou ao lado), uma seção "Feedback". Vazia até existir o primeiro feedback ou a primeira proposta de troca.
- Uma linha por card que tem mudança, com rolagem pro lado (estilo carrossel, como a primeira seção da prévia "Vibe cool" com os templates lado a lado):
  1. **Original** (como estava na versão que ela assistiu)
  2. **Última** versão proposta, logo ao lado do original
  3. Versões anteriores mais pra frente na linha
- Cada card mostra um label de classificação: "Original", "Última", "v2", "v1"... O label "Última" fica pequeno e some depois de uns segundos (não fixo), como os labels de card.
- O card é estático: a cena com todos os elementos já na tela, sem animação (economiza). Junto vai o texto final da fala.
- **Com áudio:** botão de play com a fala daquela cena (o que está na tela nem sempre explica sozinho). O original toca o trecho da voz atual (do tempo de início ao fim da cena). A proposta toca a fala nova na voz grátis (Thalita ou Andrew; se o sandbox não alcançar o serviço de voz, gerar pelo GitHub Actions como nos chats anteriores).
- Se a cena tem uma transição (muda de um estado pra outro), o card mostra dois quadros lado a lado: "começa assim" e "vira isso".
- Barato: o "antes" é cópia do trecho de HTML da cena que já existe, não é refeito.
- Embaixo de cada card, uma linha do que mudou (ex.: "saiu: plano de saúde dos ex-senadores; entrou: placar emendas x supersalários x pacote"), pra ela ver se algo sumiu sem querer.
- Botão "Usar esta" / "Juntar com o original" em cada card, que copia o pedido pra ela colar no chat.

## Quando vira card (regra dela, 12/nov/2026)
- **Vira card:** quando ela não gostou de nada de uma cena (ou do vídeo), ou quando a mudança é grande (troca o conteúdo da cena, entra ou sai um assunto, muda o argumento). Ex.: trocar a cena do Alcolumbre por um placar de emendas, supersalários e pacote.
- **Não vira card:** ajuste pequeno (explicar um termo, mudar uma palavra, tamanho, quebra de linha). Esse eu corrijo direto e conto em 1 linha. Ex.: explicar "teto de gastos" embaixo do item.

## 3. Como responder
- Toda vez que eu mandar uma prévia de reel, a resposta termina com uma linha avisando: "Feedback: me fala o card e eu respondo com a skill cards-feedback." Assim, se ela mandar feedback sem citar a skill, eu já sei que a resposta é por aqui.
- Quando ela mandar feedback: aplicar no vídeo quando for óbvio e criar o par antes e depois na aba. Quando eu estiver em dúvida, não troco no vídeo: deixo só a proposta na aba e pergunto em 1 linha.
- No chat, só: quais cards ganharam proposta e o que mudou em cada um, 1 linha cada.
- Quando ela aprovar, a versão escolhida entra no lugar da cena, o card vira "Aprovado" e fica na aba como histórico.

## 4. Relação com outras skills
- Quando ela pede auditoria completa, roda a auditoria-na-tela; as cenas que a auditoria sugere trocar inteiras viram cards aqui (antes e depois), e o resto continua como recado.
- Usa os recados e o botão de mostrar/esconder da auditoria-na-tela.
- O painel de opções (2b da auditoria-na-tela) continua valendo pra quando ela quer ver várias alternativas de visual; esta skill é pra trocas de conteúdo e conferência de antes e depois.
- Vale pra todos os skills de reel (o reel-pasta-roteiro-auditoria lista esta aba no padrão mínimo de toda prévia).