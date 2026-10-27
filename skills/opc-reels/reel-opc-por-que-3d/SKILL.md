---
name: reel-opc-por-que-3d
description: Reel explicativo da Oak Park Construction em 3D animado (Three.js determinístico) que mostra o porquê das coisas na obra residencial ou comercial com a estrutura "faz errado e vai consertando até ficar certo", cerca de 1 minuto, em inglês, com CTA de serviço.
---
# Reel OPC: Por quê? (3D)
Contexto: skills de reel da Oak Park Construction (OPC), sul da Flórida, @oakparkconstruction, licença CBC1263425. Criado em 2026-10-26, atualizado em 2026-10-27 com a análise quadro a quadro de 7 reels 3D de referência. Feito para Claude, mas qualquer IA (ex.: ChatGPT) pode ler e seguir.
Série "Why it's built this way". Uma coisa que o cliente quer ou usa (cozinha aberta, telhado, muro, loja nova) respondida com um modelo 3D que se monta errado, falha, e vai sendo consertado peça por peça até ficar certo. Pegar das referências o RECURSO (corte em seção, setas de força, câmera sempre andando, ritmo de elos), nunca o roteiro, o modelo, o visual ou as frases.
Herda do reel-opc-dica-pontilhado: regras gerais OPC, marca, voz, pastas, checklist. Resumo das regras gerais abaixo para este arquivo ser autossuficiente.
## Regras gerais OPC (resumo)
* Inglês, público EUA (sul da Flórida). Todo vídeo é educativo e mostra o que vem por trás.
* Duração ideal perto de 1 minuto (55 a 75 s); complexo até 90 a 120 s; 3 min é raro e precisa de motivo. Nunca curto e fraco: mínimo 4 elos.
* Narração 3,0 a 3,3 palavras por segundo, voz contínua, sem pausar para a ação, sem travessão.
* CTA de serviço adaptado ao tema no final. Sem isca de comentário. Sem faça-você-mesmo em estrutura.
* Fonte em toda afirmação técnica (Florida Building Code, NEC, Florida Statutes, fabricante, NOA Miami-Dade), fonte na tela.
* Pelo menos 1 em cada 5 ideias comercial (build-out, código de incêndio, acessibilidade, cobertura comercial).
## O que as referências ensinaram (2026-10-27)
* Duração: curtas de 81 a 87 s com 6 a 7 elos; longas de 147 a 165 s com 12 a 13 elos. Cada elo dura 10 a 12 s. Ritmo 2,8 a 3,3 pps em português.
* A ação começa no quadro 1 (telhado voando, terra sendo cavada, carvão pegando fogo). Nenhuma abre com logo.
* Corrente fixa: óbvio → falha visível → solução → nome técnico. A falha sempre aparece NA IMAGEM (racha, empoça, enverga, tomba) antes da solução.
* Força desenhada antes da solução: setas de peso, empuxo, vento, água acumulando.
* Corte em seção para mostrar o invisível: dentro da parede, embaixo do chão, dentro do aparelho.
* Número vira imagem: "30% = sobe 30 cm a cada metro", "quase 2 m de parede".
* Personagem simples dá escala e emoção (reage, se assusta, aponta).
* Uma frase contraintuitiva ("parece estranho, mas...").
* A melhor delas embute uma dica que muda decisão do cliente ("na reforma dá pra derrubar parede, mas pilar não se toca"). A OPC faz isso SEMPRE.
* Fraquezas que a OPC corrige: CTA só de engajamento, nenhuma fonte, temas e normas brasileiros.
## Estrutura padrão: "faz errado, conserta até ficar certo"
1. 0 a 3 s: o modelo já está em cena e alguém faz do jeito errado ou barato (derruba a parede, empilha bloco sem aço, abre loja sem sistema). Algo acontece na hora (racha, cede, entra água, alarme).
2. Elos 2 a 5 (ou até 7): "Problem: [falha]. So we [solução]. That's the [termo]." A peça certa entra em lima #CBCC10 exatamente na palavra falada, com rótulo HTML preso ao 3D.
3. Dica de decisão do cliente em um dos elos (o que perguntar, o que exigir, quando precisa de licença).
4. Fecho: objeto inteiro girando com as setas de força agora fluindo certinho + "And that's why [X] is built this way." + CTA de serviço.
5. Um assunto por reel. Se passar de 7 elos, dividir em parte 1 e 2.
## Como fazer o 3D (determinístico, sem IA de vídeo)
* Three.js no HTML da prévia (CDN cdnjs). Modelos low-poly com primitivas, estilo maquete de argila: materiais foscos, lima só na peça em destaque, cinza quente nas demais, fundo preto com pontinhos, luz suave e sombra de contato. NÃO usar o visual colorido saturado das referências.
* Recursos: setas de força animadas (peso descendo, vento empurrando, água subindo), corte em seção (clipping plane), explosão de camadas, rachaduras e água como efeito, partículas para chuva/fumaça/poeira, rótulos HTML presos ao 3D com linha-guia, pílula de estado em creme ("WATER POOLS HERE", "3 TONS").
* Câmera sempre em movimento lento (órbita ou dolly); corte seco só na troca de elo.
* Personagem: quando fizer sentido, o Mike cartoon (ver reel-opc-mike-cartoon) como escala e reação, em billboard 2D dentro da cena 3D.
* Tudo comandado pelo relógio da trilha: render(t) puro, para o MP4 sair igual à prévia (Playwright quadro a quadro, preserveDrawingBuffer true).
* Kit de peças reutilizáveis: parede com montantes, viga/header, bloco CMU com célula grauteada e vergalhão, tie beam, treliça com strap, laje com vergalhão, janela com caixilho, sapata, telhado, porta corta-fogo, coifa comercial, placa EXIT.
* Plano B sem WebGL: isométrico 2,5D em CSS.
## Conteúdo
* Exemplos do sul da Flórida: CMU + tie beam, HVHZ, impacto, chuva forte, lençol alto, sal.
* Trocar tudo que for brasileiro pelo equivalente dos EUA (DR → GFCI; laje maciça de casa → trusses; telha de barro 30% → telhado em HVHZ com produto aprovado).
* Comercial: build-out de loja e restaurante, saídas e sinalização, acessibilidade (ADA / Florida Accessibility Code), sprinklers, coifa Type I, separação corta-fogo entre lojas, certificate of occupancy.
## O que não copiar das referências
* Frases-assinatura ("Se você...", "Essa é a...", "Parabéns! Você construiu um...").
* Visual low-poly saturado, casa cinza com porta marrom, legenda branca palavra a palavra igual, rótulo amarelo, boneco de camiseta amarela.
* A mesma ordem de elos de um tema já feito por eles.
* Isca "comente X".
## Checklist
* Falha visível no 1º segundo; nada parado enquanto a voz fala.
* 4 a 7 elos, 55 a 75 s (ou justificativa), 3,0 a 3,3 pps.
* Dica de decisão do cliente presente.
* Rótulos 3D sem sobreposição em nenhum quadro-chave; texto legível no celular.
* Fonte na tela para cada número ou código.
* CTA de serviço ligado ao tema.
## Referências capturadas (inspiração, nunca copiar)
Pasta-mãe no Drive: 19SIHYkGYM3EsaudQUGtnYLmhVTYfMkZh. Folhas de quadros-chave: subpasta _ANALISE_FRAMES_2026-10-27.
* IG DezX76zgi47 telhado, 165 s, 13 elos: https://drive.google.com/drive/folders/1ML0vr-LJ_GdNzcG66TmbdBOXAwnNc1wY
* IG De4oWvEh06y arranha-céu, 147 s, começa errado e melhora: https://drive.google.com/drive/folders/1Yjc30Q1cqURILnE42oza6xQ-xnkA2P-1
* IG De65azIs6Vk bunker, 84 s: https://drive.google.com/drive/folders/1kcTH72R9vEH9rsaBouIc_gOMRBBLfuwr
* IG DeuPPkvySMu laje, 84 s: https://drive.google.com/drive/folders/1BXueot-WxidcaW7K7eiStFVtNTMQlHry
* IG DenEOh1vIIl chuveiro elétrico, 87 s: https://drive.google.com/drive/folders/16s4yiIDA3rx9M_Au9JMhsaHYlfgIrMZG
* IG De1by9FSefx muro de arrimo, 81 s: https://drive.google.com/drive/folders/1tCwUNpZkMQ1f7cbRBhMfAsSrVuIhEhza
* IG DerOHtAtkl5 churrasqueira (marcada como piscina), 86 s: https://drive.google.com/drive/folders/18dPXnFBtH3MFHfFELDLN7ZL_XgPs52Zq
Status: análise feita em 2026-10-27 (ver doc SKILLS_REEL_OPC, seção ATUALIZAÇÃO 2026-10-27).
