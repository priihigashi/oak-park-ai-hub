---
name: "coolonizacao"
description: "Acabamento cool/editorial (fotos P&B, sticker recortado, papel, cor do dia num detalhe) por cima de qualquer formato de reel, mais o template Elenco P&B e o formato de checagem pausa e explica."
---

# Coolonização

Não é um estilo novo e NÃO substitui nada. É um acabamento padronizado que vai POR CIMA da skill de formato escolhida (pontilhado cinético, colagem, timeline, desabafos, motion limpo, doodle, livro ilustrado, estilo por referência...). Objetivo: sair da vibe fofinha/engraçadinha pra uma vibe cool, editorial, Gen Z, com cara de feita por gente e não "feita com IA".

## Regra nº 1: não perder conquistas
Tudo que já foi aprovado nos outros reels continua valendo e vence esta camada em caso de conflito:
- Ciclo da reel-pasta-roteiro-auditoria (pasta, ROTEIRO com lista de feedback, TRANSCRIÇÕES, tracker, auditoria do ChatGPT, revisão visual), roteiro-storytelling, auditoria-dissonancia (político), reel-zona-segura, reel-som, reel-fechamento, auditoria-na-tela (recados leves na criação).
- Prévia com velocidades, pulos de 5/10/30 s, caixa de anotações com marcar tempo e copiar, aba do vídeo original, download, legenda e 1º comentário.
- Legenda de 2 linhas cheias com a palavra atual na cor do dia, banner de 0:50, CTA final, tamanhos mínimos (letra miúda 23 px, notas 24 px, fonte 22 px), conteúdo ocupando a tela até a legenda.
- CTA final de News com a frase padrão, sempre igual: "Pra ajudar a aumentar o engajamento, copia o link, curte, reposta aqui e nos stories, e segue a página pra não perder o próximo." Ícones entrando na palavra, nesta ordem: Copia o link, Curte, Reposta, Segue (sem Salva). Vale igual na coolonização BR e é conferido na auditoria-na-tela.
- Pessoas: recorte só de cabeça com contorno branco grosso, nome + partido + chip de ideologia; sem recorte quando o clipe da pessoa está na tela.
- Fonte do kit: Rubik 800/900 + JetBrains Mono. Não trocar.
Tudo que esta skill trouxer tem que MELHORAR a base, nunca piorar. Se uma ideia daqui vale pra todos os reels, sugerir a ela atualizar a skill base também.

## Quando usar
- Ela fala "coolonizar", "versão cool", "vibe cool", "deixa mais cool".
- Sem pedido, NÃO aplicar.

## Passo 0: referências (quando ela mandar reels de inspiração)
- Baixar o reel (caminhos que já funcionaram: navegador do app no Mac com folha de quadros via canvas, ou capture_pipeline.yml / workflow temporário tmp-* com yt-dlp no oak-park-ai-hub, apagando o branch no fim).
- Print de CADA tela: ffmpeg com detecção de troca de cena (`select='gt(scene,0.3)'`) + 1 quadro a cada 2 s nas cenas longas. Folha de quadros salva em News > Templates > Estilos e Referências, subpasta "Coolonizacao".
- Ficha curta: como tratam as fotos, texturas, cores, tipografia, ritmo, como texto e imagem entram. Copiar o jeito, nunca a cena, personagem ou marca. Crédito a quem serviu de referência só com aprovação dela.

## Tratamento de imagem (o coração da vibe)
Três camadas, sempre nessa ordem:
1. **Fundo: foto real em P&B.** Pessoas reais de corpo inteiro, cenas, detalhes (uma boca aberta, mãos, plenário, multidão). P&B com contraste alto, granulado e, se quiser, pontilhado. Pode virar loop curto (2–4 quadros ou trecho de vídeo em P&B).
2. **Frente: objeto recortado.** Foto pública recortada ou objeto "quase real" gerado por IA (desenho realista mas não fotográfico: urna eletrônica, cofre, carteira de trabalho, microfone), com a mesma textura por cima pra parecer impresso.
3. **Por cima de tudo: textura de papel** (multiply ~50%) + granulado. É isso que tira a cara de digital/IA.

**Diferencial dela: a cor.** As referências são quase só P&B. Aqui entra a cor do dia, pouca: num detalhe (bloco atrás do objeto, uma palavra do título) ou o objeto colorido sobre o fundo P&B. Nunca a tela toda colorida. Político pula azul e coral.

## Como conseguir cada imagem (nessa ordem)
1. **Foto pública real, em mais de um banco (nunca só um):** Wikimedia Commons (API com `filetype:bitmap`; dá 429 se baixar rápido, esperar ~1 s entre arquivos), Agência Brasil (CC BY, creditar), Planalto, Câmara, Senado, Flickr com licença Creative Commons, rawpixel domínio público, Unsplash, Pexels e Pixabay (gratuitos; a API pede chave, então pelo navegador ou pedir a chave a ela), Openverse (busca vários bancos de uma vez; bloqueou no workbench, tentar do shell ou do Mac). Fotos do álbum dela só com autorização. Pra cada imagem, juntar 3 a 4 opções e mostrar lado a lado (folha de contato) antes de escolher; foto temporária também tem que combinar com a fala. Anotar licença e autor no ROTEIRO; crédito no 1º comentário quando a licença pedir. Se o shell não alcança, workbench do Composio ou branch temporário (apagar depois). Rostos de políticos: primeiro a pasta "Políticos · Fotos" no Drive de News.
2. **Recorte:** rembg (birefnet-portrait pra pessoa, isnet-general-use pra objeto) com alpha_matting=True (fg 240, bg 10, erode 10). Depois o tratamento P&B + papel.
**Regra de custo (dela, 12/nov/2026):** por padrão só imagem GRATUITA (passos 1 e 2). IA paga (Replicate) só depois que ela aprovar, cena por cena. No relatório da prévia, listar o que achei de grátis e o que recomendo gerar em IA, e esperar o ok dela. Quando esse fluxo for automatizado, essa conversa de aprovação continua existindo.
3. **Não achou exatamente o que quer? Não travar:** pôr a melhor imagem temporária e marcar com recado 🔁 "Imagem temporária · recomendo refazer em IA" + o que a imagem final deveria mostrar (formato da skill auditoria-na-tela). Seguir o vídeo; a troca vem na conversa.
4. **Gerar em IA (só com o ok dela; recomendado pra objetos e cenas que não existem em foto):** flux-1.1-pro pelo replicate_batch.yml (disparado via Composio GITHUB_CREATE_A_WORKFLOW_DISPATCH_EVENT). Prompt-base: "semi-realistic illustration of <objeto>, isolated on plain flat white background, soft studio light, slightly painterly, not photographic, high detail, centered with margin, no text, no logos". Recortar por flood-fill do branco ou rembg. Se não der pra gerar aqui, passar a ela o prompt exato pro ChatGPT + link da pasta de inspiração.
- Nunca a mesma imagem duas vezes no vídeo. Nunca selo "imagem gerada por IA" na tela.
- Sem rembg pesado no workbench do Composio (tem 1 GB de RAM e o processo morre): lá, recortar objeto de fundo claro por flood-fill da borda (scipy) e deixar o rembg pro shell local ou pro runner do GitHub.
- Banco de stickers e fundos já tratados: Drive News > Templates > Estilos e Referências > Coolonizacao (1irSarOY8CL_xK4SFgHoCn_d2ZW-GBxhl), com fontes_e_licencas.json. Reaproveitar antes de buscar de novo; cada imagem nova tratada entra lá com a licença.

## Stickers e movimento (regra de transição)
- Sticker = recorte P&B com contorno de papel claro (~14 px), sombra curta deslocada e textura por cima.
- Entrada "pop de papel": cai de cima girando uns 8°, quica 1 vez e assenta torto (−4° a 6°). Saída saindo de cena, nunca sumindo no lugar.
- Na tela, todo sticker respira: balanço lento de 1° a 2°, sombra junto.
- Profundidade: foto de fundo anda devagar (zoom de ~10% na cena), stickers andam o dobro, texto fica parado. Parece 3D sem ser.
- Troca de cena por corte seco no ritmo da fala, ou por cortina (bloco preto ou de papel passa e já traz a cena nova). Nada de dissolver.
- Recorte do fundo: o plenário (ou o cenário) some e só as pessoas recortadas ficam, viram stickers e vêm pra frente.
- Entradas de 0,3 a 0,5 s com freada no fim; nada fica parado mais de 2 s sem algo se mexer.

## Transição da palavra-chave vazada
Quando a fala chega na palavra-chave do assunto (ex.: "qualificação" na pergunta "você acha que elas não estão lá por falta de..."): a cena mostra a foto/pessoas, a tela escurece, e a palavra entra gigante ocupando a tela, quebrada em linhas (QUA / LIFI / CA / ÇÃO), com a foto P&B vista POR DENTRO das letras (background-clip: text). A última linha pode vir na cor do dia. Letra com borda de tinta borrada e levemente imprecisa (filtro SVG: turbulência + deslocamento leve + blur de 1 px + corte de alfa).

## Nossa identidade x a da referência (não copiar)
Referência de vibe: página doantidoto (só como inspiração, nunca citar nem copiar). O que ELES fazem e a gente NÃO copia: a fonte deles (grotesca condensada borrada), palavra partida com hífen (HIPÓ-TESE, LIBER-DADE), legendinha amarela pequena no meio, capa só de palavra gigante no preto. O que é NOSSO:
- Fonte do kit (Rubik 900) com o nosso filtro de tinta; palavra quebrada SEM hífen (regra de quebra dela continua).
- Mais animação: eles quase só usam foto. A gente mistura foto/sticker com as cabeças recortadas, as pessoinhas andando e elementos 3D.
- Um pouco de cor (a cor do dia num detalhe), mais tech.
- **Diferencial principal: personagem 3D entre as camadas.** Foto mais atrás, sticker mais à frente, e um personagem 3D (cabeça real recortada em corpo de terno, regra do reel-3d-historinha) que ANDA entre elas, mostrando a profundidade e contando a história: assina a lei na frente, anda pra trás e muda o preço na bomba de gasolina lá no fundo, sai de cena e volta na próxima cena; ou carrega a caixa de precatórios pro ano seguinte. O personagem pode ser o próprio político de quem o vídeo fala, e pode fazer a troca de cena. Gráfico também pode ganhar um pouco de 3D. Construir em HTML (Three.js) sempre que der; Blender só se o HTML não chegar lá.
- Ela gosta de misturar estéticas: não forçar uma só. A coolonização é o acabamento comum que deixa a mistura com cara de uma página só, inserida aos poucos.

## Fase 2 (depois, não agora): Oak Park Construction
Versão pra OPC com o Mike: cabeça real do Mike num corpo 3D, entrando na cena pra apresentar e corrigir ("não usa esse material, usa esse", "esse tá errado, esse tá certo"). É uma das opções de formato OPC, junto com as que já existem.

## Acabamento cool (igual em qualquer estilo)
- Fundo: papel cru (#F2EEE6) ou quase preto (#0B0B0C). Nada de pastel ou gradiente colorido.
- Uma cor de destaque só (a cor do dia) + preto/branco (vermelho continua de apoio).
- Título grande em Rubik 900, tracking um pouco apertado, linhas equilibradas, com o filtro de tinta borrada nos títulos grandes. Metadados em JetBrains Mono: EP.xx · TEMA · data, fonte (respeitando os tamanhos mínimos).
- Entrada de texto por máscara (a palavra sobe de dentro da linha) ou digitação, entrando na palavra falada; nada de bounce ou pop fofo.
- Elementos editoriais: linha de metadados no topo, letreiro rolando (ticker) com fonte/assunto, chips de borda fina, barras de progresso.
- Pontilhado como textura (máscara suave, girando ou pulsando devagar).
- Ritmo: cortes mais secos, menos elementos por tela, sem deixar vazio acima da legenda.
- Proibido (cara de IA): gradiente roxo/azul, brilhos, ícones genéricos, sombra suave em tudo, emojis decorativos, carinhas fofas, tudo centralizado e simétrico.

## Layout aprovado (ela, 12/nov/2026: "gostei pra caralho")
**A · Janela:** fundo = a própria foto da pessoa em pontilhado grande P&B ocupando a tela toda, com papel e grão por cima; metadados em mono no topo (EP.xx · TEMA · data); título grande em 2 linhas, 1ª em branco-papel e 2ª na cor do dia; embaixo, a foto real numa janela retangular larga. Vale COM a faixa na cor do dia saindo de trás da janela (deslocada pra cima/direita) e SEM a faixa (só a janela). Ela gostou das duas e também da foto colorida na janela sobre o fundo P&B. Prints guardados na prévia (seção "Aprovados").
Variações criadas a partir dele, pra testar: **B · Polaroid torta** (foto com borda de papel girada ~−3°, fita na cor do dia), **C · Pontilhado na cor do dia** (pontos coloridos no preto, foto num círculo com aro de papel), **D · Foto em cima, título embaixo**.

**Contraste automático:** texto sobre foto tratada sempre mede o fundo atrás dele; fundo escuro = texto branco-papel (#F7F4EE) com sombra suave, fundo claro = texto quase preto. Nunca preto no pontilhado escuro (erro que ela apontou).

## Fábrica de stickers (eu produzo, ela escolhe)
Pra cada pessoa, objeto ou cena da história, eu mesmo faço o sticker do começo ao fim:
1. **Buscar a imagem** gratuita (ordem da seção "Como conseguir cada imagem"). Político: pasta "Políticos · Fotos" primeiro.
2. **Recortar o fundo** com rembg no shell local (isnet-general-use, alpha matting) ou no runner do GitHub. Workbench do Composio só com flood-fill (pouca RAM).
3. **Tratar em várias versões** e mostrar lado a lado na prévia (laboratório de stickers): P&B com papel, cor original, pontilhado, duotone (preto + cor do dia), xerox (alto contraste com grão). Pode ainda: só granulado, só textura, só contorno. Contorno de papel ~10–14 px e sombra curta deslocada em todos.
4. **Movimento** (escolher por cena; uns ficam estáticos, outros não): parado, respira (balanço leve), zoom lento, desliza pro lado, pop de papel (cai, quica, assenta torto), tremidinho de papel. Na prévia, menu pra ela trocar tratamento, movimento e fundo.
5. Guardar cada sticker pronto (com licença) no banco da pasta Coolonizacao do Drive pra reusar.
Sem foto boa grátis: sticker temporário + recado 🔁 recomendando IA; IA só com o ok dela.

## Fundo de papel que ela aprovou
A textura que ela curtiu é papel "de verdade": grão fino irregular + fibrinhas curtas (não textura falsa repetida), e combina com o pontinho. Vale em qualquer cor: papel cru, preto papel, cor do dia, vermelho, azul royal; com ou sem pontilhado em degradê. Receita: ruído por pixel ±13 + manchinhas raras + ~700 traços curtos de fibra a 10% de opacidade; pontinho com raio caindo a partir de um ponto de luz.

## Acentos e til nas palavras gigantes
Em palavra grande com máscara/recorte (palavra vazada, entrada por máscara), o til e o acento ficam acima da caixa da letra e são cortados: usar entrelinha ≥ 0,95, um respiro em cima (padding-top ~0,06em) e máscara final com folga (clip-path inset negativo em cima, ~-30%). Conferir no print todas as palavras com Ã, Õ, Á, É, Ç antes de entregar.

## Transições prontas (na prévia de referência)
- Palavra-chave vazada: letras entram nítidas, o borrão de tinta só chega depois da última linha e fica uns segundos. Opções dentro das letras: foto P&B com ou sem borrão, pontilhado P&B, pontilhado na cor do dia.
- Cortina de papel rasgado: o papel sobe com borda rasgada e traz a cena nova.
- Pontos que crescem: o pontilhado na cor do dia cresce até fechar a tela e vira a cena nova.
- Pop de papel do sticker.
- Cena 3D entre camadas: fundo pontilhado atrás, objeto 3D no meio (ex.: urna), sticker real na frente, personagem de terno com cabeça recortada que entra, anda pra trás, age (aperta o CONFIRMA, a tela acende na cor do dia) e sai; câmera com paralaxe leve. Feito em Three.js (cdnjs r128) dentro da prévia.

## Referências de movimento (só pra tirar ideias, não trocar o estilo)
Reel instagram.com/p/De9f9xygFTW: acelerado demais e carregado (não copiar o ritmo), mas tem ideias de transição, fundo com pontilhadinho e um personagem falando (melhor que os que eu já fiz, ela ainda quer melhor). Baixar e tirar prints pelo Mac ou pelo workflow do GitHub.

## 2D ou 3D
O diferencial é o 3D de verdade, mas 2D continua valendo. Quando ela quiser gastar pouco, fazer a cena em 2D primeiro e trocar por 3D depois, se ela pedir.

## Template Elenco P&B (12/nov/2026, vale pra qualquer tema: Brasil, EUA, OPC)
Várias pessoas reais na mesma cena, em P&B, saindo da base da tela em camadas. Fica salvo na prévia da coolonização (arquivo elenco.html + seção "Template novo"); toda rodada atualiza lá E no artefato do tema, e eu devolvo os dois links.
- **Sem cabeça com contorno branco neste template** (ela: "as cabecinhas são o problema", "não misturar com tracejado"). Cabeça com contorno continua valendo nos outros formatos.
- **Camadas:** atrás = corpo inteiro/meio corpo com desfoque leve (~1,6–1,8px) e um pouco mais escuro (ela adorou o desfoque); meio = quem é o foco; frente = meio corpo saindo da base da tela.
- **Braços:** retrato oficial já vem cortado no ombro na foto original. Nunca usar retrato com corte lateral como meio corpo solto. Ou fica atrás de alguém que esconde os ombros, ou recebe esfumado nas bordas e na base (máscara lateral 0–14% e 86–100% + base). Meio corpo e corpo inteiro só com foto que mostra os braços inteiros (ex.: braços cruzados, braço levantado, comício). Detectar automático: alpha encostando na borda lateral no terço de baixo = corte lateral.
- **Rosto:** conferir cada recorte ampliado antes de usar. Foto de rua/multidão perde rosto ou nariz no recorte (o fundo se mistura): trocar de foto em vez de entregar. Recorte com pedaços soltos (plateia, cabeças) = cortar reto acima ou manter só o maior componente.
- **Etiquetas discretas:** sem caixa de fundo. Nome em Rubik 800 ~13px com sombra de texto; embaixo partido em 11px e só a ideologia num pill pequeno colorido (precisa ser legível em fundo colorido; texto vermelho em fundo laranja some).
- **Títulos:** com a fonte real (Rubik 900) tudo fica bem mais largo; título de capa ~29px pra caber em 2 linhas cheias. Linha de fonte em 1 linha só.
- **Seletor de cor na prévia:** laranja, mostarda, terracota, ferrugem, oliva, vinho (outono). Muda 2D e 3D juntos.
- **3D:** as mesmas camadas da capa em profundidade de verdade, saindo da base (sem chão aparecendo), fundo pontilhado na cor mexendo devagar, sombra das pessoas no fundo. Nada de cabeça flutuando nem busto em cima de chão.
- **Pontilhado:** bolinha pequena (ela pediu menores), não grade grossa.
- **Transições na prévia:** tocam quando aparecem na tela (IntersectionObserver) e repetem sozinhas; nunca só uma vez no carregamento.

## Formato de checagem "pausa e explica" (12/nov/2026)
- Pessoa falando (vídeo com fundo recortado) na esquerda, não centralizada. À direita, nome quebrado em linhas, estado/partido e ideologia, e o assunto em poucas palavras, tudo estruturado numa coluna.
- Legenda de 2 linhas EM CIMA da cabeça, puxada pro lado esquerdo, com a cor seguindo a fala.
- Pausa: ícone de pausa, a pessoa vai pro fundo em ARCO (curva, não reta), diminui até o centro, fica mais escura e com desfoque leve; o bloco de nome/assunto sobe e centraliza no topo; gráfico (barras crescendo uma depois da outra) e fonte entram na frente, com narração.
- Volta: tudo sai, aparece o play e ela volta pela mesma curva; o texto volta pro lado. Na prévia a volta é automática depois de ~4 s de dados, e também tem botão.
- Vídeo livre: Wikimedia Commons (filetype:video), recorte quadro a quadro no runner do GitHub. birefnet em 720p é lento demais (40+ min); usar u2net_human_seg em 540p (~5 min). Se o vídeo já tiver legenda gravada, cortar o quadro acima dela e esfumar as bordas. Comprimir pra ~1 MB (VP9 com alfa) antes de embutir.
- Sugestão de série: "3 melhores e 3 piores frases" de cada figura principal, misturando quem virou e quem segurou; frase com dado errado = pausa e explica no meio.

## Animação casada com a fala (reclamação repetida dela, 12/nov/2026)
O acabamento cool não vale nada se a tela não acompanha a voz. Antes de montar, mapa de batidas com o tempo de cada palavra; cada coisa citada entra NA palavra. Peças prontas que funcionaram no reel do PLP 299:
- **Ícones de linha por item falado:** SVG de traço branco (stroke 6, pontas redondas) com 1 detalhe na cor do dia, dentro de um bloquinho de borda fina; entram um por um com pop curto (0,3–0,45 s). Ex.: prédio de colunas (governo), fábrica (empresas), alfinete (estados), soja/minério/carne, prédios pequeno/médio/grande com selo (JÁ FORA, POUPAR, COBRAR), microfone + chapéu (show sertanejo).
- **Selos ENTRA / NÃO ENTRA / QUASE NÃO ENTRA:** pill colado DEPOIS do nome, antes do valor. ENTRA = verde cheio, NÃO e QUASE NÃO = vermelho cheio com letra branca (os dois iguais).
- **Placar que conta + carimbo + etapas ("a decisão ainda não acabou"):** números sobem até o resultado, carimbo torto "TEXTO-BASE APROVADO" entra por cima e SAI quando aparecem as etapas (✓ feito → próxima → depois), que ficam.
- **Pizza de 1/4:** círculo com uma fatia na cor do dia acendendo na palavra "um quarto".
- **Barra de escala pra número abstrato:** ex.: teto R$ 46,3 mil (barra longa) x salário mínimo R$ 1.621 (barra minúscula) com "28 vezes menos".
- **Pessoa entra na hora do nome:** foto/recorte com data-at no tempo do nome, na mesma fileira das outras pessoas da cena.

## Estilos de edição criativos (14/nov/2026, valem aqui, no Cool BR, OPC, UGC e, quando couber, News)
- **Texto atrás de quem passa:** recortar a pessoa quadro a quadro e deixá-la passar NA FRENTE do texto. Só em cena em que ela se move pela tela (atravessa de um lado pro outro, ou vem pra frente e cruza a altura do texto); antes e depois o texto fica inteiro e legível. Pode cortar no momento em que ela chega na altura do texto. Nunca em pessoa parada ou sempre centralizada (aí o texto vai na frente ou mais acima, fora da cabeça). 1 ou 2 vezes por vídeo, não em todas as cenas.
- **Estrela ou sticker no rosto:** nunca da mesma cor (nem parecida) do texto da cena; cor de contraste.
- **Comemoração:** na conquista, explosão de estrelinhas de 4 pontas coloridas + som de celebração bem baixinho.
- **Sticker animado com sentido:** o sticker é do tema (bicicleta, não patinete) e tem um detalhe que mexe (a roda se solta e gira).
- **Bonequinhos de palito** fazendo a ação da cena (andando de bike, rodas girando) passando pela parte vazia da tela.
- **Doodle só com sentido:** nada de seta ou curva solta que não aponta pra nada.

## Conferência antes de mandar (aprendido 12/nov/2026)
- Tirar print de CADA tela sozinha, com a fonte de verdade carregada (Rubik/JetBrains via fontsource embutida no teste), não com fonte substituta: sobreposição só aparece com a fonte real.
- Conferir: nada saindo da tela, nada em cima de rosto, título em 2 linhas cheias, broche/cor seletiva visível no peito, sem área vazia grande.
- Ela percebe pressa: melhor entregar menos telas bem acabadas do que muitas com sobreposição.

## Checklist antes de entregar
- [ ] Nenhuma regra já aprovada nos outros reels foi perdida?
- [ ] A skill base ainda é reconhecível?
- [ ] Fundo em foto real P&B + objeto recortado + papel por cima?
- [ ] A cor aparece só num detalhe (ou só no objeto)?
- [ ] Imagens temporárias marcadas com recado (e só elas)?
- [ ] Nenhum elemento fofo sobrando?

## Referência visual
Prévia inicial (3 direções, teste de tratamento de foto e exemplo de recados): https://claude.ai/artifact/GiKHumpZ5G7j1QmtuTT5mm
Reels de inspiração que ela mandou: instagram.com/reel/DfpK21XRzPD e instagram.com/reel/DfcI2Auxa1z (prints de cada tela ainda pendentes: o Instagram bloqueia download na nuvem; fazer pelo Mac ou pelo workflow do GitHub). Print do perfil deles que ela mandou em 12/nov/2026 mostra a estética geral (palavra gigante borrada no preto, fotos P&B com luz de cinema, papel). Quando ela escolher a direção favorita, atualizar esta skill com ela como padrão.