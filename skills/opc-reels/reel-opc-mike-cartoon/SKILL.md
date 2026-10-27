---
name: reel-opc-mike-cartoon
description: Série de reels da Oak Park Construction com o Mike (Michael McFolling, PM) em cartoon, cabeça de foto real e corpo desenhado, construindo a obra fase por fase com som, fumacinha e "puf", na estrutura "faz errado e vai consertando", cerca de 1 minuto, em inglês, com CTA de serviço.
---
# Reel OPC: Série do Mike (cartoon)
Contexto: skills de reel da Oak Park Construction (OPC), sul da Flórida, @oakparkconstruction, licença CBC1263425. Criado em 2026-10-27. Feito para Claude, mas qualquer IA (ex.: ChatGPT) pode ler e seguir.
O Mike (Michael McFolling, project manager da OPC) vira o personagem fixo da marca: cabeça de foto real recortada + corpo cartoon desenhado. Ele entra em cena, constrói cada fase com ferramenta e som, algo dá errado ("oh no"), ele conserta, a fase fica pronta com um "puf", e no fim ele anda pela obra pronta e aponta. A voz conta a história sem parar; o Mike nunca fala em cima da narração (a voz é de fundo, como se fosse ele).
Inspiração principal: IG De1by9FSefx (muro de arrimo) e o formato de corrente das outras 6 referências. Recriar temas em versão americana, nunca copiar.
Herda do reel-opc-dica-pontilhado (marca, voz, pastas) e do reel-opc-por-que-3d (estrutura e kit de peças).
## Regras gerais OPC (resumo)
* Inglês, público EUA (sul da Flórida). Todo vídeo é educativo: responde uma necessidade do cliente ou algo que ele gosta de fazer sem saber o que vem por trás, e mostra o que vem por trás.
* Duração ideal perto de 1 minuto (55 a 75 s); complexo até 90 a 120 s; 3 min raro e justificado. Nunca curto e fraco: mínimo 4 fases.
* Narração 3,0 a 3,3 palavras por segundo, contínua, SEM pausar para a ação (a ação acompanha a voz, não o contrário). Sem travessão.
* CTA de serviço adaptado ao tema no final (ex.: "Want to build with us? Get in touch.").
* Fonte em toda afirmação técnica, na tela. Sem faça-você-mesmo em estrutura.
## O personagem
* Cabeça: foto real do Mike, recortada (rembg isnet-general-use + alpha matting), contorno branco 6 px, levemente maior que o normal (cabeça 1,3x, estilo caricatura gentil). Só com fotos que o Mike aprovou.
* Kit de expressões (uma foto para cada; pedir à Priih se faltar):
  1. sorrindo (padrão, entrada e fim);
  2. trabalhando de costas (só o boné/nuca; usar quando martela ou serra);
  3. "oh no" (surpresa, boca aberta) quando algo falha;
  4. concentrado (olhando para baixo, medindo);
  5. orgulhoso/apontando (fecho).
* Corpo: vetor/cartoon simples em SVG, camiseta preta com logo OPC lima, calça cinza, botas, capacete branco opcional por cima da foto. Membros em peças separadas para animar (braço do martelo gira no ombro, pernas alternam ao andar).
* Escala: o Mike ocupa cerca de 1/3 da altura da tela quando está trabalhando; a obra é o foco.
* Sempre com EPI quando serra ou martela; nunca em situação contrária às normas de segurança.
## Movimentos e efeitos (biblioteca)
* Entradas: pela esquerda andando, pelo topo descendo de corda/escada, pela direita correndo. Alternar; nunca a mesma entrada duas vezes seguidas.
* Ação de construção: martelar (3 batidas no ritmo da fala), serrar (vai e vem + serragem), carregar bloco, despejar concreto, apertar parafuso.
* Som: batida de martelo, serra, "clunk" de bloco, "whoosh" do vento, "puf" na conclusão. Volume de efeito 20 a 30% abaixo da voz. Bibliotecas livres (Pixabay, Freesound CC0), crédito no story doc.
* Fumacinha/poeira: nuvem cartoon creme saindo enquanto ele trabalha.
* "Puf": nuvem cobre a área por 0,3 s e some revelando a fase pronta (peça nova em lima por 1 s, depois cor normal).
* Falha: tremida da câmera 0,2 s + rachadura vermelha #FF4A3D + rosto "oh no".
* Fecho: o Mike anda pela obra pronta e APONTA para cada peça enquanto a voz recapitula em uma frase (rótulos acendem na ordem).
## Estrutura do episódio
1. 0 a 3 s: o Mike já entra fazendo do jeito fácil/errado (empilha bloco sem aço, quer derrubar parede). A falha aparece no máximo no segundo 6.
2. 4 a 6 fases: "Problem: ... So we ... That's the [termo]." Cada fase 8 a 12 s: entrada ou continuação → ação com som → "puf" → rótulo.
3. Uma dica de decisão do cliente em uma das fases.
4. Recap andando e apontando (6 a 8 s): a corrente inteira em uma frase (ex.: "Roof to straps, straps to tie beam, tie beam to filled cells").
5. CTA de serviço com o Mike sorrindo e logo OPC.
## Cenário
* Fundo: lote do sul da Flórida em estilo flat (palmeira, céu, chão creme com pontinhos), vista lateral em corte para mostrar o que fica dentro da parede/chão.
* Estilo diferente das referências 3D: aqui é 2D cartoon flat, sem low-poly.
* Fase 2 da série (depois): o boneco do Mike sobre FOTOS REAIS de projetos (ex.: manta de impermeabilização), voz de fundo como se fosse ele. Usar o reel-opc-obra-real para as fotos.
## Como produzir (determinístico)
* HTML + SVG + GSAP (ou CSS keyframes) na prévia, tudo comandado pelo relógio da trilha: render(t) puro; MP4 via Playwright quadro a quadro, igual ao pontilhado.
* Assets do Mike num kit reutilizável no Drive Marketing: /OPC Mike Kit/heads/*.png, /body/*.svg, /sfx/*.mp3.
* Voz: rascunho edge-tts en-US-AndrewMultilingualNeural (rate +10%); final ElevenLabs só após aprovação; futuro: clone de voz do Mike só com autorização escrita dele.
## Temas bons para a série
* Por que casa no sul da Flórida é de bloco de concreto (filled cells, tie beam, straps, impacto).
* Addition do começo ao fim (fundação, bloco, tie beam, telhado).
* Quintal: deck, cerca de piscina, luz, drenagem.
* Comercial: o Mike monta uma loja vazia até virar restaurante aprovado.
* Seawall/drenagem de lote (paralelo americano do muro de arrimo).
## Checklist
* O Mike entra fazendo algo no quadro 1; falha até o segundo 6.
* Expressão certa em cada momento (sorriso, costas, "oh no", apontando).
* Voz nunca para; efeitos abaixo da voz.
* 4 a 6 fases, 55 a 75 s, 3,0 a 3,3 pps.
* Recap andando e apontando + CTA de serviço.
* Fonte na tela para cada código/número.
* Fotos do Mike aprovadas por ele.
