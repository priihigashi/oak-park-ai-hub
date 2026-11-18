---
name: "reel-split-videogame"
description: "Reel em tela dividida com explicação em cima e historinha de videogame (bonecos arredondados, moedas, contadores) no meio. Use quando Priih pedir split screen 3D videogame, historinha didática ou jogo."
---

# Reel split screen "videogame" (texto em cima, historinha no meio)

Nasceu no reel "De onde dá pra tirar" (PLP 299, ajuste fiscal, nov/2026), na cena do JCP com a dona Maria. Serve pra explicar um conceito difícil (imposto, juros, desconto) pra quem não entende nada: a voz conta uma historinha e o jogo mostra cada passo enquanto ela fala.

Referência viva: artifact "De onde dá pra tirar · v3 split jogo" (https://claude.ai/artifact/TyGTNT9e7PhhZpmNei8dYQ). O código-fonte fica dentro dele em src/ (game.py, build2.py, common.py, tpl2.html, tokens.json, script.json, shot2.py, mid_shot.py).

**Vibe:** usar SEMPRE junto com o skill coolonizacao (cool vibe: fontes grandes, mais corpo do que capa, visual premium). O jogo é arredondado e moderno (claymorphism leve, degradês suaves, sombras macias). Nada "Nintendo demais", nada pixel art, nada infantil demais.

Vale junto com: coolonizacao, reel-pasta-roteiro-auditoria, reel-zona-segura, reel-som, roteiro-storytelling e a regra de voz (grátis Thalita até a aprovação final, ElevenLabs só 1 take).

## 0. Orçamento de fala (ler antes de escrever qualquer frase)
A regra de cada item é **o que é, quanto dá e quem segura**. Todo o resto vai pra tela (fala de impacto, chip, letra miúda), não pra voz.
- **Teto do vídeo:** mirar em 2:00 a 2:30. Passou de 3:00, cortar FALA (nunca o item). Em 3:30 a 4:00 já está errado. Só usar fala de processo se sobrar muito tempo.
- **Orçamento por item:** 15 a 25 s (~35 a 55 palavras com rate +12%). A historinha principal (a que ensina o conceito) pode ter até ~35 s (~85 palavras). Contar as palavras de cada cena ANTES de gerar a voz (~3,2 palavras/s).
- **Fala de processo é desperdício:** quem pediu, quem relatou, quem disse o quê em qual noite, quem tirou da pauta, placar de votação. Isso vira cabeça com chip na tela, sem narração. Na voz, no máximo meia frase de responsabilidade ("a bancada do agro pressionou, e o relator, do PT, tirou").
- **CTA em 2 s:** uma frase só e só no fim ("Salva essa lista. Os links tão na bio."). Nada de explicar cada opção ("se quiser votar sim, vota sim; se quiser mandar e-mail..."). Não repetir o CTA no começo.
- **Nunca acelerar a voz pra caber no tempo.** Já errei: atempo 1.1 levou o vídeo a 3:46 e ela não entendeu nada. Se não cabe, a fala está longa: reescreva.
- **Sugestão é de terceiros.** Nunca "a gente sugere", "a gente achou", "conta nossa" na voz. Use "tem quem sugira", "tem quem aponte", e só se alguém de fato propôs (buscar antes). Que é estimativa nossa fica só na letra miúda.
- **Gancho com pergunta aberta:** se tem uma parte que preocupa (ex.: o que o pacote faz com a educação), prometer na abertura ("no final eu conto...") e entregar no fim.

### Exemplo ("De onde dá pra tirar", nov/2026): de 799 pra 458 palavras, de 4:12 pra ~2:25, sem tirar nenhum item
- JCP, ANTES (237 palavras, 1:08): salário dela, "se tivesse pego no banco", "como se rendesse na poupança", "o leão só morde 17", Simples até 4,8 mi, lucro real acima de 78 mi, por que banco usa mais...
- JCP, DEPOIS (84 palavras, ~30 s): "A dona Maria pôs 1 bilhão dela numa rede de padarias e lucrou 100 milhões. O leão levaria uns 34. Mas a lei deixa ela fingir que emprestou esse bilhão pra própria empresa e pagar juros pra si mesma. Esses 50 milhões saem antes do imposto, e o governo perde uns 8 milhões. Todo ano. Padaria pequena nem pode usar. Quem mais usa são empresas grandes e bancos. Acabar com isso daria uns 10 bi por ano." Os limites 4,8 mi e 78 mi continuam GRANDES na tela.
- Militares, ANTES: 57 palavras com "o próprio governo propôs" e "projeto parado" em frases separadas. DEPOIS (36): "Militares vão pra reserva, a aposentadoria deles, com 35 anos de serviço, em média aos 48 anos. O governo propôs idade mínima de 55, uns 2 bi por ano, e o projeto tá parado na Câmara."
- CTA, ANTES: 30 palavras no fim + 13 no começo. DEPOIS: 10 palavras, só no fim.
- Teste rápido de cada frase: se eu tirar esta frase, o leigo deixa de entender o item? Se não, ela vai pra tela ou sai.

## 1. Antes de tudo: o exemplo tem que ser VERDADEIRO pra regra
O exemplo da história precisa ser alguém que de fato pode usar o que está sendo explicado. Erro já cometido: explicar o JCP com uma "padaria", sendo que padaria pequena (Simples) nem pode usar. Conserto: "rede de padarias", com valores em milhões. Sempre MOSTRAR o LIMITE com número (ex.: Simples até R$ 4,8 milhões/ano não pode; lucro real, obrigatório acima de R$ 78 milhões/ano e pra todo banco, pode). O número vai grande na tela. Na voz basta "padaria pequena nem pode usar; quem mais usa são empresas grandes e bancos". O porquê ("o desconto cresce com o dinheiro parado, e banco é obrigado a guardar muito") fica na letra miúda, a não ser que sobre tempo.

## 2. O MAPA da historinha (obrigatório, antes de desenhar)
1. **Tabela de passos:** frase da narração | palavra-gatilho | o que entra | o que sai | qual número muda, dentro de qual objeto | qual fala de impacto aparece.
2. **Mapa de posições:** cada objeto com x, y, largura e altura. Conferir que nada se sobrepõe em NENHUM passo. Texto dentro de objeto nunca passa de x 915 (botões do Reel cobrem x > 930 a partir de y 1060).
3. **Tempo mínimo na tela:** todo texto/banner fica pelo menos ~1,5 s visível. Erro já cometido: na cena das LCI/LCA, 2 banners passaram tão rápido que ninguém via.
4. Mandar print do momento mais cheio antes de caprichar.

## 3. Regra de ouro: como num videogame, o número fica DENTRO da coisa
- Todo valor fica escrito dentro do objeto que recebe ou perde dinheiro (pote, sacolinhas, saco do leão, saco do milhão). Nada de rótulo solto em cima ou do lado.
- Dentro do objeto: nome pequeno em cima ("LUCRO R$", "SALÁRIO R$", "JUROS R$", "LEÃO R$") e o número gordinho embaixo (Rubik 900). O objeto é grande o bastante pro número caber COM FOLGA; conferir no print ampliado.
- **Escrever com a palavra: "R$ 34 mil", "R$ 1 milhão"**, nunca com um monte de zeros.
- O número muda ali dentro (sobe ou desce como cronômetro) com moedas voando de um objeto pro outro. Durante a contagem, número inteiro, sem vírgula (só o valor final pode ter, ex.: 8,7 mil).
- Todo dinheiro que a narração cita ganha número (ex.: "ela tira o salário" → a sacolinha do salário enche até R$ 30 mil).
- **Cores das sacolinhas:** todas da mesma cor (verde = dinheiro) e muda só a cor da letra (1 milhão vermelho, salário verde-claro, juros amarelo). A do leão é bege com número vermelho.
- **Contraste:** nada de branco junto com vermelho sobre verde. Letra colorida com contorno/sombra PRETA. Fundo amarelo = texto preto; fundo meio cheio (pote) = branco com contorno escuro.
- Nenhum objeto com fundo ou caixa preta atrás: tudo recortado.

## 4. Falas de impacto no espaço vazio (não é uma segunda legenda)
- No espaço entre a frase-guia e o jogo, centralizada e o mais perto possível do jogo sem encostar.
- Só PALAVRAS DE IMPACTO, sempre UMA linha (white-space:nowrap), Rubik 900 ~58px, branco com o trecho importante em amarelo. Nunca repetir o que a legenda diz. Medir a largura de cada uma (≤ 765 px).
- Números com setinha na MESMA linha: "Juros: 0 → 50 mil", "🦁 34 mil → 17 mil". Nunca número numa linha, seta em outra.
- Exemplos aprovados: "Salário: R$ 30 mil", "Lucro: R$ 100 mil", "Do banco? Normal ✓", "O dinheiro é dela", "Empréstimo de mentira", "Governo: −8 mil", "Todo ano. Pra sempre.", "Nunca devolve", "Quem mais usa: bancos".

## 5. Layout do palco (1080x1920)
De cima pra baixo:
1. Cabeçalho e placar (y 268+).
2. Título em 2 linhas cheias + frase-guia do passo com número.
3. Falas de impacto.
4. Jogo (div .game, top ~720): chão elíptico (~860 px, x 110 a 970).
5. Faixa que rola (ticker) logo abaixo do chão, da mesma largura do chão: letra miúda escrita simples.
6. Legenda falada centralizada, MESMA fonte do @ (Rubik), peso 600, ~44px, 2 linhas por página.
7. Faixa "toque pra continuar" (0:50 a 1:00) entre a legenda e o @.
8. @tentandochegaratevoce Rubik 800 28px à direita (não mexer no tamanho sem ela pedir) e a fonte logo abaixo, com folga pra não cortar.

## 6. Personagens (anatomia e camadas)
- **Senhorinha:** coque em cima → cabelo de trás → rosto → franja só na metade de cima, terminando ACIMA dos óculos (erro já cometido: cabelo nos olhos). Fica sempre na frente de tudo (z-index maior) e nunca escondida atrás de objeto. Braço que acena num grupo separado. Quando a história é de empresa grande, ela pode ganhar um blazer.
- **Bicho que representa o governo/imposto (o leão):** PESSOA com cabeça de bicho: de pé, terno azul-marinho, camisa branca, gravata vermelha, óculos redondos, juba fofa, focinho com nariz, boca em "w" e bigodinho. Segura a sacolinha dele na frente do corpo. Pode ficar de três quartos olhando pra personagem (perfil total esconde óculos e boca).
- **Boca que abre:** a boca é um elemento próprio que estica pra baixo a partir da borda de cima (transform-box:fill-box; transform-origin no topo; scale vertical), com dentinhos. Erro já cometido: mover a boca inteira fez ela "descer e subir".
- **Cuidado com !important:** transform com !important anula animação CSS. E a classe da animação precisa ser mais específica que .g.pop.on (usar .g.x.mv.on).
- Conferir cada boneco ampliado (recorte do print) antes de montar a cena.

## 7. Movimento
- **Algo surge de algo:** o saco do milhão faz um CAMINHO EM CURVA (arco, keyframes) até o meio do chão, some num puff de fumacinha com brilhos amarelos, e a padaria aparece ali. Nada de só aparecer.
- Contador que importa desce enquanto o outro sobe, ao mesmo tempo, com moedas voando dos dois lados (recalcular --dx/--dy sempre que mover um objeto).
- Balão de fala curto ("☝️ Não, não!") acima da personagem, sem cobrir nada.
- Calendário bonitinho: de mesa, com duas argolas, cabeçalho na cor do tema, ano grande preto em página branca, e a página vira (flip) a cada ano.
- Placar: quando a narração fala "vamos somar junto e manter um placar", o placar aparece GRANDE no meio da tela e depois fica pequeno no canto.

## 8. Abertura do reel
- Intro em ~5 a 10 s, direta, sem mudar a informação. Números grandes do mesmo tamanho (ex.: 50 BI e 35 BI); frase do meio grande (~96px, 2 linhas) e cada parte entra na SUA palavra ("Tira uma parte da saúde" → "e dos estados"), nunca as duas juntas.
- Erro já cometido: a tela dizia "Sai da saúde" depois de a fala ter sido corrigida pra "uma parte". Quando a fala muda por causa de fato, conferir o texto da TELA da mesma cena.
- Sem chamada pro print no começo (repete o fim e gasta tempo). No lugar, se houver, a promessa do final ("no final eu conto o que preocupa a educação").

## 9. Voz e técnica
- Voz grátis edge-tts pt-BR-ThalitaMultilingualNeural rate +12% no Composio REMOTE_WORKBENCH (o shell local não alcança o Bing). Transferência: upload_local_file → GOOGLEDRIVE_UPLOAD_FROM_URL (source_url, name; account priscila) → mcp Google_Drive download_file_content. Se o arquivo for pequeno, colocar um pad.bin de ~120 KB no .tar pra o resultado ser salvo em arquivo.
- Trocar só um trecho: gerar a frase nova, cortar o silêncio, emendar com ffmpeg (wav 24 kHz mono → mp3 96k) e deslocar os tempos das palavras seguintes.
- **Sempre copiar a voz nova pra pasta publicada** (pub/voz.mp3) e mudar o ?v= do src, senão a prévia toca o áudio velho e tudo parece fora de sincronia.
- Cada objeto é um div .g com data-in/data-out em segundos (gatilhos de palavra), classes pop/drop/popbig e handlers: data-cls, data-fill, data-num + data-fmt ("{} mil"), data-years.
- Gatilho de número: se a palavra exibida muda ("R$ 34 mil"), o gatilho vira o começo normalizado ("r34").
- Pra conferir animação no meio (puff, rugido, curva), pausar a animação e setar currentTime antes do print.
- Auditoria Playwright em cada passo: sobreposição, zona segura, número vazando do objeto, largura das falas.

## 10. Como trabalhar com ela
- Mudar só o que ela pediu. "Usa aquela fonte" = usar a que já está lá, sem mexer em outras coisas.
- Se não entender um pedido, perguntar em uma frase antes de mudar tudo (erro já cometido: trocar "34 mil" por "34.000").
- Pedidos no meio do trabalho: fazer todos e atualizar este skill com a lição.
- Conferir as contas que aparecem na tela e saber explicá-las (ex.: 50 mil de juros − 17,5% = 41,25 mil; governo perde 34 − (17 + 8,75) ≈ 8 mil).

## 11. Sementinhas na narração
- Frases extras que entram depois (contexto, contraponto, dado a mais) vão primeiro pra TELA (fala de impacto ou letra miúda). Só entram na voz se cabem no orçamento da seção 0. Se entrarem, ficam curtas e no máximo +5% de velocidade (base +12% → +17%); nunca acelerar o vídeo inteiro.
- Cada sementinha ganha uma fala de impacto na tela e, se for estimativa nossa, a nota vai na faixa que rola ("~6 bi por ano é estimativa nossa").

## 12. Estudo de caso: como a história do JCP evoluiu (usar pra criar e pra auditar cada história)
**v1 (não funcionou):** "Juros sobre capital próprio. A empresa paga os sócios e ainda desconta esse pagamento do imposto dela, uma coisa que só existe no Brasil. Acabar com esse desconto daria uns 10 bi por ano."
O que ela questionou, na ordem, e o que virou regra:
1. "Só existe no Brasil" era falso (a Itália tinha até 2024). → Nunca afirmar exclusividade sem checar.
2. "Não absorvi nada, me dá um exemplo." → Termo técnico sempre vira historinha com personagem, objeto e número.
3. Dúvidas que ela teve como leiga, uma por uma: o que é normal e o que é o truque; o salário entra onde; por que empréstimo de banco é normal; como a empresa justifica e prova; o que é "render como poupança"; por que acabar com isso; quem não pode usar; por que se repete todo ano e nunca acaba. → Cada dúvida virou um passo da história. Antes de construir, listar as dúvidas que um leigo teria e garantir um passo pra cada uma.
4. "Quem mais usa são os bancos": por quê? qual o limite? tem número? → Sempre dar o limite com número (Simples até R$ 4,8 mi/ano não pode; lucro real, acima de R$ 78 mi/ano e todo banco, pode), o porquê em uma frase e um número de tamanho (um banco grande ~R$ 6 bi/ano, estimativa).
5. "A gente usou um exemplo errado": padaria pequena nem pode usar. → O exemplo tem que ser alguém que pode usar a regra (rede de padarias, valores em milhões).
6. "Fala da Itália/França?" → Não citar país de fora (vira gancho pra "olha os protestos lá"). Comparar a REGRA: "raro no mundo; lá fora, quando existe, vale só pro dinheiro novo".
7. "Só 2 países tinham e tiraram" também era falso (o Chipre tem até hoje). → Toda frase de comparação internacional passa por busca antes de entrar.
8. Na tela: números dentro dos objetos, falas de impacto curtas, nada de segunda legenda, nada escondido, tudo sincronizado com a palavra.
**Como auditar uma história nova:** (a) o exemplo é elegível pra regra? (b) cada dúvida de leigo tem um passo? (c) toda afirmação tem fonte e não é "só no Brasil" sem checar? (d) tem limite com número e o porquê de quem mais usa? (e) alguma frase dá gancho pra desviar o assunto? (f) as contas fecham?