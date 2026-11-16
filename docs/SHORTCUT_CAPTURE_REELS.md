# Atalho permanente — Capture de Reels

**Abrir:** https://github.com/priihigashi/oak-park-ai-hub/actions/workflows/capture_pipeline.yml

Este repositório já contém o **Capture Pipeline v2**, com captura de links do Instagram, TikTok e YouTube, download e transcrição via Whisper. Antes de pedir upload manual ou sugerir um serviço externo para transcrever um reel, verificar este fluxo.

## Como usar

1. Abrir o link acima, selecionar **Run workflow**.
2. Em `url`, colar a URL completa do reel.
3. Em `project`, escolher `brazil` para reels políticos brasileiros.
4. Em `mode`, escolher **`transcribe_only`** quando a intenção for apenas transcrever/verificar (não publicar nem criar tarefas).
5. Em `notes`, informar o contexto da checagem.
6. Executar e conferir os arquivos/transcrições de saída no Drive e o status da execução no Actions.

O conector GitHub deste chat pode ler o código e as execuções, mas **não oferece atualmente o acionamento manual `workflow_dispatch`**. Nesse caso, fornecer o link do Actions para execução pelo usuário, em vez de alegar ter rodado o Capture.

## Caso de referência — Lula x Moro, tríplex (15/11/2026)

- Reel: https://www.instagram.com/reel/DfuwXyqqvf4/
- `project`: `brazil`
- `mode`: `transcribe_only`
- `notes`: `Transcrever integralmente; comparar com STORYTELLING e ESTUDO DE CASO Lula x Moro triplex no Drive; identificar fatos que fortalecem ou enfraquecem a acusação; avaliar parte 2 sem alterar o roteiro atual.`

Não confundir o mecanismo de captura existente com a possibilidade de executar GitHub Actions pelo conector atual.
