---
name: "reel-doodle-sobre-foto"
description: "Reel com desenho de linha por cima de foto real (linha branca estilo Dr. Propolus, preta estilo Koketit, colorida estilo Dribbble). Use quando a Priih pedir doodle sobre foto ou desenho na foto."
---

## Durabilidade e versão ChatGPT · 18/11/2026
Esta é uma cópia versionada para ChatGPT/Codex; o original fica em `../original/`. Antes de concluir uma alteração, preservar nova versão no Drive Creations > Tools, Skills & Flows > Skills > Reels e Carrosséis > formato > ChatGPT (usar as pastas existentes criadas por Claude) E no GitHub privado `priihigashi/news`, em branch/PR sem merge. Conferir arquivo, pasta, tamanho/hash e links nos dois destinos; registrar pendência real se algum falhar. Nunca considerar apenas o arquivo local como entrega durável; GitHub não substitui Drive. Não sobrescrever versões existentes nem alterar a versão Claude. Consultar `MANIFESTO.json` e o índice desta entrega para origem e comprovantes.

As regras atuais de `regras-priih` prevalecem sobre conflitos históricos abaixo, inclusive aprovação antes de MP4 e voz paga. Os arquivos locais citados no texto histórico não são presumidos disponíveis no celular. Dependências preservadas separadamente em `compartilhadas/`, sem fundir os formatos.


# Reel doodle sobre foto

Um estilo, uma skill. Junta três referências parecidas:
- Linha branca (Dr. Propolus, Ilias Walchshofer): sobre foto escura, continua o contorno de um objeto real até ele virar outra coisa.
- Linha preta (Koketit, Shira Barzilay): sobre foto clara, transforma nuvem, onda ou veio em personagem. Muitas referências dela têm nudez: usar só como referência de traço.
- Colorida (coleção Dribbble "Doodle on Photos"): foto pequena tipo polaroid, setinhas com legenda à mão, brilhinhos e corações. Boa pra UGC e tema com criança.

Referências no Drive: Estilos e Referências > Desenho sobre foto 17lHt4DUHVPJPdJc1WvmaBKriY8o9pJIn. Exemplos aprovados como ponto de partida: Bomba chorando, Bloco vira casa, O rio do mármore e Gelatina com as crianças em https://claude.ai/artifact/BkybeH3vq5z9zPmSh9CLFd.

## A regra que faz ficar bom
O desenho tem que NASCER da foto: seguir a mangueira, os blocos, o veio da pedra, a borda do prato. Desenho solto por cima fica básico (foi a crítica dela na primeira versão). Antes de desenhar, marcar na foto os contornos que vão virar desenho.

## Visual
- Linha de pincel que afina nas pontas e varia (função stroke do template), com segunda passada fina deslocada pra parecer lápis.
- Linha branca em foto escura, preta em foto clara. Escurecer topo e rodapé da foto pra título e legenda.
- Animar como se estivesse sendo desenhado (o traço avança), elementos pequenos entram com mola.
- Cobrir marca de terceiros na foto com um elemento desenhado (balão, nuvem).

## Fotos
- OPC e UGC: da biblioteca dela (álbuns de cada obra e "UGC, vídeos caseiros e produtos"). No Mac só tem a versão pequena de muitas fotos (o resto está no iCloud): pra reel final, pedir a original ou usar a do Drive da OPC.
- News: foto livre (Wikimedia) com crédito no rodapé, ou foto do momento.
- Rosto das crianças: perguntar antes de usar em post público.

## Variação UGC com vídeo pessoal (aprovada em 14/nov/2026, Bike sem pedal)
Template pronto: https://claude.ai/artifact/WE5tG4ZwAkNbZinPWCnsLu (v11). Pasta: UGC > Content > v1_balance-bike. Começar daqui para qualquer UGC com vídeo das crianças.
- Letra: título serifado grosso creme #F7EFA0 (Fraunces 800, itálico na palavra-chave) com brilhinhos de 4 pontas piscando em volta, sem fundo, mais uma retícula leve por cima do vídeo (mesmo visual B do Cool BR). Nada de fonte gordinha nem caixa atrás.
- Frase fixa que explica o produto (ex.: "Balance bikes teach kids to ride without training wheels") embaixo, na mesma fonte e sem fundo, ficando um tempo longo no começo. Conferir quadro a quadro e mostrar só nos trechos em que não cobre as crianças. Linhas com white-space:nowrap, nunca uma palavra sozinha na linha.
- Rosto: estrela de 4 pontas gordinha (sem rosto aparecendo entre as pontas), uma cor por aparição, grande (~2,4x a largura do rosto), como camada por cima do vídeo (nunca queimada no vídeo), com tracking quadro a quadro (Haar + CSRT, conferir os recortes) e adiantada ~0,08 s, com controle de ajuste na prévia. Cobrir crianças, ela e o Mike (todo adulto da família que aparece de rosto).
- Doodle tem que ter sentido na cena: nada de seta ou curva solta. Celebração (explosão de estrelinhas coloridas + sininho bem baixinho) no momento da conquista e no momento orgulho dos pais.
- Cada texto mostra o que diz: se o texto fala das duas bikes (rosa e azul), a cena tem que mostrar as duas juntas. Manter a ordem por lugar (rua com rua, corredor com corredor).
- Cena com problema (criança trava, sai do quadro) sai do corte. Ela marca trechos ruins do clipe: usar só o intervalo que ela liberar.
- Último take do vídeo mais longo (~4 s).
- Sticker que tenha a ver com o tema, nunca um objeto parecido (patinete no lugar de bicicleta). Melhor ainda: sticker animado com detalhe, como a roda da bike que se solta e gira.
- Bonequinhos de palito andando de bicicleta (rodas girando, pernas empurrando) passando por baixo na cena de lado combinam com UGC.
- Uso: versão doodle sem sticker = post principal; versão com stickers = Reel de teste.
- Áudio: som original baixinho + música calma; manter incentivos falados quando houver.

## Estilos de edição criativos (14/nov/2026)
- **Texto atrás de quem passa:** recortar a pessoa quadro a quadro e deixá-la passar NA FRENTE do texto, só em cena em que ela se move (atravessa a tela ou vem pra frente e cruza o texto); antes e depois o texto fica legível. Nunca em quem fica parado ou centralizado (aí o texto vai na frente ou mais acima). 1 ou 2 vezes por vídeo.
- **Estrela no rosto nunca da cor do texto** da cena; cor de contraste.
- Comemoração com estrelinhas + som baixinho na conquista; sticker animado do tema; bonequinhos de palito fazendo a ação.

## Código do template (copiar daqui)
- Drive, pasta "/motion" 1LLgeWSABpgBd8n1VoVti19vaYV834XuM: template_9-exemplos_4-estilos.html 1JqCvM8KhHfQX01dRhDKaIrGpua7hqLvz (exemplos Bomba chorando, Bloco vira casa, O rio do mármore, Gelatina). Prévia: https://claude.ai/artifact/BkybeH3vq5z9zPmSh9CLFd
- As fotos não vão junto no HTML: buscar de novo na pasta de origem.

## Lições do reel "iPhones do Senado" (10/nov/2026)
- Tempo de leitura: nenhum texto entra no último meio segundo de uma cena, e todo texto fica na tela o tempo de ler. O build tem um audit automático que puxa o texto pra mais cedo e marca !! no audit.txt; zerar os !! antes de publicar.
- Resposta a outra pessoa: desmentir logo no começo, nunca validar a raiva dela antes.
- Texto dentro de balão ou caixa sempre centralizado, com o mesmo respiro dos dois lados (grifo colorido não encosta na borda da caixa).
- Linhas equilibradas: ajustar o tamanho da fonte pra que as linhas fiquem parecidas (ex.: "Poderes não poderão ser superiores" numa linha só, em vez de deixar "Executivo federal." sozinho no fim).
- Eixo único por cena: se o elemento principal está no centro (porta, diagrama), título e textos da cena também ficam centralizados. Alinhar à esquerda só em cena toda em coluna.
- Respiro entre desenho e texto: texto não encosta no desenho; se faltar espaço, diminuir/subir o desenho.
- Diagrama de pessoas: título numa linha só quando couber, cabeça de cima subindo pra perto do título, nome centralizado embaixo de cada cabeça (sem "·" sobrando no fim da linha), linhas ligando cabeça a cabeça sem cortar texto, chip de partido sempre visível.
- Nada acima de y=268, a não ser uma faixa fixa proposital (ex.: a faixa amarela do começo).
- Clipes do vídeo de outra pessoa: pré-cortar e pré-acelerar (nik_*_play.mp4, keyframe a cada 10 quadros) pra prévia não travar no iPhone.
- Balão ou desenho e o texto dele entram juntos, no mesmo instante.
- Frases curtas na tela: primeiro nome, ideologia e função ("Davi, direita, presidente do Senado").
- Narração: cortar pausas longas (compress.py) sem acelerar a voz.

## Revisão obrigatória depois da primeira montagem (sem ela pedir)
Assim que o vídeo existir, antes de mostrar: print do ÚLTIMO quadro de cada cena (tudo na tela) e olhar um por um procurando sobreposição, texto que deveria estar centralizado, linha desequilibrada ou palavra sozinha, texto encostando em desenho ou na legenda, bloco amontoado com buraco embaixo, e frase na tela repetindo a legenda. Corrigir e repetir até limpar. Também revisar o primeiro minuto da narração procurando frase lenta ou longa que dá pra dizer mais rápido sem tirar conteúdo.

## Como fazer
Seguir reel-pasta-roteiro-auditoria, reel-zona-segura, reel-som e reel-fechamento. Conferir quadros com Playwright antes de publicar a prévia.