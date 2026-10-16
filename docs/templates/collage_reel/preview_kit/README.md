# Preview kit — prévia ao vivo do reel (artifact) + layout sem sobreposição

Episódio de referência: "Querida amiga" (qamiga.html). Prévia publicada: https://claude.ai/artifact/GFQ8SVUf8NmyEb5UNz2VVN

- `gen.py` — gera a página do reel a partir do timeline.json (tempos por palavra da narração).
- `../layout.js` — empilhamento automático: `data-flow="grupo:ordem"`, `data-ftop`, `data-gap`, `data-dy`, `data-nosize`, `data-minh`. Espaço uniforme, sem sobreposição; mede depois que as fontes carregam.
- `../engine.js` — `data-thou="1"` nos contadores = separador de milhar (1.571).
- `../fx.js` — legenda `.kar.karfull` = frase inteira na tela, só a cor anda.
- `mkpreview.py` — monta a prévia publicável: palco 1080x1920 escalado dentro de `#scaler` (não escalar `#stage`: o shake sobrescreve), áudio `narracao.mp3` como relógio (`render(audio.currentTime)`), Play, barra de busca, velocidades 1/1,2/1,5/2/3x.
- `overlap_check.js` — varre o vídeo a cada 0,25 s e lista sobreposições e elementos fora da margem segura (ignora animações em andamento).
- `prep2.py` / `mix2.py` — timeline a partir das falas (atempo 1,5) e mix com trilha/SFX.
