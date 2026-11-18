---
name: reel-editorial-guiado
description: Criar prévias verticais de estudo ou apresentação de uma página, site ou documento com títulos cinéticos, recortes reais, gráficos simples e voz grátis, no estilo editorial da prévia PLP299 v4. Usar para repetir esse design, não como formato genérico de todo conteúdo News.
---

## Durabilidade e versão ChatGPT · 18/11/2026
Esta é uma cópia versionada para ChatGPT/Codex; o original fica em `../original/`. Antes de concluir uma alteração, preservar nova versão no Drive Creations > Tools, Skills & Flows > Skills > Reels e Carrosséis > formato > ChatGPT (usar as pastas existentes criadas por Claude) E no GitHub privado `priihigashi/news`, em branch/PR sem merge. Conferir arquivo, pasta, tamanho/hash e links nos dois destinos; registrar pendência real se algum falhar. Nunca considerar apenas o arquivo local como entrega durável; GitHub não substitui Drive. Não sobrescrever versões existentes nem alterar a versão Claude. Consultar `MANIFESTO.json` e o índice desta entrega para origem e comprovantes.

As regras atuais de `regras-priih` prevalecem sobre conflitos históricos abaixo, inclusive aprovação antes de MP4 e voz paga. Os arquivos locais citados no texto histórico não são presumidos disponíveis no celular. Dependências preservadas separadamente em `compartilhadas/`, sem fundir os formatos.


# Reel editorial guiado

Produza uma prévia de apresentação compreensível e reproduzível, com o design da referência aprovada. Se houver regras pessoais de conteúdo disponíveis, leia-as antes; o pedido atual determina tema, duração e escopo.

## Referência e base

- Leia [processo-v4.md](references/processo-v4.md) ao planejar estética, ritmo, voz, legendas e transporte da prévia.
- Copie `assets/base-v4/` para uma **nova pasta/versionamento**. A base tem HTML/CSS/JS, dados, imagens incorporadas, fonte e voz da peça antiga. Não altere os assets da skill.
- A base é exemplo visual, não um modelo editorial pronto para publicar. Substitua fatos, cifras, capturas, links, identidade, narração, tempos e textos de postagem da peça anterior. Não reaproveite promessas de privacidade sem conferir o novo produto.

## O que caracteriza este design

Palco 1080×1920, 9:16; Manrope bold; títulos grandes em linhas equilibradas; amarelo, vermelho, escuro e branco; textura pontilhada discreta; recortes reais com borda e sombra sólida; carimbos inclinados e SVG. Blocos entram com retorno elástico suave; títulos revelam palavras; barras crescem na fala. Alternar composições sem transformar tudo em cartões iguais.

Use capturas autênticas ou gravação se o pedido exigir. Não apresente uma montagem de capturas como filmagem contínua. Valores e gráficos exigem fonte, período, hipótese e distinção entre fato, estimativa e proposta. O texto integral de um documento não deve ser confundido com leitura de trechos.

## Produção e revisão

Escreva narração contínua e planeje a ordem visual antes de montar. A referência dura 46,464s e tem 12 cenas; isso é exemplo, não quantidade obrigatória. Para pedidos como o original, manter 35–50s sem acelerar a voz para caber.

O processo real usou Python para preparar dados, HTML/CSS/JavaScript e SVG para a prévia, e `edge_tts` com `pt-BR-ThalitaMultilingualNeural` para voz grátis e WordBoundary. Se esse serviço não estiver disponível, use alternativa gratuita autorizada e registre a mudança. Não consuma voz paga para reproduzir a base. Música opcional da referência é síntese simples via Web Audio, não faixa licenciada.

Recalcule duração, páginas de legendas e entradas a partir da nova voz. Não basta trocar `fala.txt`: os horários da base são explícitos. Mantenha duas linhas legíveis, palavra atual destacada e áreas seguras. Ofereça play/pausa, busca, saltos, velocidades, notas e textos para copiar. Confirme reprodução completa, áudio e cada cena em celular e desktop; buscar uma posição deve reconstruir o quadro correto.

Entregue prévia com todos os arquivos necessários ou uma página autocontida compatível com o destino. O `index.html` da base depende dos arquivos vizinhos. Preservar versões anteriores; MP4 ou voz paga somente após aprovação aplicável. A skill não concede autorização para publicar, enviar mensagens, acessar contas ou alterar configurações externas.


### Entrega no celular · 16/11/2026
Antes de entregar uma prévia à Priih, fornecer URL HTTPS acessível fora do computador, testar sem sessão autenticada e conferir áudio, clipes, busca e layout móvel no endereço hospedado. localhost, caminhos locais e ZIP no Drive são apoio técnico, nunca o único link para assistir no celular. Manter o endereço da peça nas revisões.
