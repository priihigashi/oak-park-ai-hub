# Cena "anim" (rodada 4)

Contrato: o manifesto ganha `{type:'anim', start, end, module:'/previews/news-assets/<ID>/v<N>/cena-XX.js', sha256}`
(validado em news-codex/lib/news-flow.js). O módulo exporta `montar(palco, params) -> {desenhar(t), duracao}`;
`desenhar(t)` é função pura do tempo: o player chama com `audio.currentTime - start` a cada quadro.
Por isso busca, velocidade e o MP4 (depois do Sim) usam a mesma linha do tempo.

Provado aqui (prova_anim.py, roda no CI): quadro por busca = quadro por play (diferença máxima 2 de 255 por
antialias, 0% de pixels acima de 16); nenhum trecho parado acima de 3 s; tira de contato gerada.

PENDENTE (rodada 5): ligar o tipo "anim" no player /reel do Painel (repo painel-da-manha) e o teste de aceite
no celular dela com o Mac desligado (abrir, tocar, buscar, mudar velocidade, salvar nota e reler).
A cena é DEMONSTRAÇÃO TÉCNICA, não conteúdo: o visual final segue coolonizacao-br + ritmo-de-cor.md.
