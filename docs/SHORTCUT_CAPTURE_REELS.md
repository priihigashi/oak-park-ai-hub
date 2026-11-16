# Atalho permanente — Capture e criação de conteúdo a partir de reels

## Objetivo
Repetir o fluxo já usado com Claude: usuário envia **link + instrução de estilo**; o agente captura, transcreve, confere contexto, arquiva fonte e produz material reutilizável para criar post/reel mais tarde. Nunca publicar sem pedido explícito.

## Execução existente
- Workflow: https://github.com/priihigashi/oak-park-ai-hub/actions/workflows/capture_pipeline.yml
- Script: `scripts/capture/capture_pipeline.py`
- Download: `scripts/capture/video_downloader.py`
- Transcrição: `scripts/research/transcription.py`
- Modo `transcribe_only`: transcrição e frames no Drive, sem entrada na biblioteca, calendário, fila ou automações de conteúdo.
- Modo `capture`: fluxo completo e efeitos adicionais; não usar para um pedido só de pesquisa sem aval explícito.
- Ponte por issue: `.github/workflows/capture_from_issue.yml` usa workflow_dispatch com `transcribe_only`. Conferir autor da issue e o Actions; não afirmar sucesso antes do resultado.

## Padrão de solicitação pelo ChatGPT
Quando receber um link e descrição de estilo:
1. Identificar projeto, público, tom, formato, duração, CTA, conteúdo existente e regras visuais.
2. Criar um registro com link original e ID do reel; recolher legenda/autor/data se acessíveis.
3. Acionar Capture por uma via comprovada; se o conector não disponibilizar execução, criar issue de ingestão e verificar se disparou. Não dizer que transcreveu sem arquivo.
4. Ler transcrição integral e separar citações literais, alegações, fatos comprovados, incertezas e possíveis erros.
5. Pesquisar fontes primárias e registrar URLs/data de consulta. Não inventar referência ou fala.
6. Salvar **pacote de referência** na pasta correspondente do Drive: transcrição, evidências, avaliação editorial, briefing criativo e proposta de roteiro (se solicitado).
7. Para conteúdo posterior, reutilizar o pacote e o estilo aprovado; não reconstruir do zero; manter histórico de correções.
8. **Não publicar/agendar** automaticamente.

## Contrato do pacote de referência
Arquivo sugerido: `REFERENCIAS_REEL_<id>_v1` com:
- Origem: reel, link, autor, duração, data, status de download
- Transcrição integral com tempos (quando disponível) e avisos de palavras incertas
- Resumo fiel e tese do autor; distinção entre afirmação e prova
- Matriz de verificação: alegação | confirmação | fonte primária | confiança | contexto omitido
- Conexão com conteúdo anterior: o que repete | o que acrescenta | o que corrige
- Direção criativa: estilo fornecido | público | gancho | sequência de cenas | visual | narração | CTA
- Restrições editoriais e riscos de interpretação
- Links para material final e histórico de versões

## Pedido Lula x Moro, 15/11/2026
- Reel: https://www.instagram.com/reel/DfuwXyqqvf4/
- Projeto: `brazil` / @tentandochegaratevoce
- Objetivo: transcrever, verificar se fortalece ou enfraquece a tese de propina do tríplex e decidir se rende parte 2.
- Fontes internas: documentos no Drive `STORYTELLING · Lula x Moro, triplex` e `ESTUDO DE CASO · Lula x Moro, triplex`.
- Separar **reserva/reforma do imóvel**, **vantagem pessoal**, **ligação a propina/Petrobras**, **validade processual**.
- Estilo editorial: português simples, público amplo; fatos e visual juntos, cena a cena; apresentar evidências favoráveis e desfavoráveis; sem afirmar culpa ou inocência judicial inexistente.
- Estado da solicitação: roteiro e estudos localizados; reel ainda não foi baixado/transcrito neste atendimento.

## Atenção ao acervo
A planilha antiga `1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU` está marcada `ZZ_ARQUIVADO · só consulta, não escrever`. Não colocar novas entradas nela. Buscar destino atual antes de gravar.

## Se algo falhar
Informar qual etapa falhou, preservar link e briefing e apontar o próximo passo concreto. Não oferecer ferramentas externas antes de checar o Capture do GitHub.
