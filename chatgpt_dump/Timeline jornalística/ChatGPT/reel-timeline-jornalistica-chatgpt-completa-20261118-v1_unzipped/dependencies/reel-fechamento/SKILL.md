---
name: "reel-fechamento"
description: "Use logo depois que um reel ou post for publicado (ou quando a Priih achar um erro num post que já está no ar): guarda tudo na pasta, atualiza tracker e aba de collabs, salva a fonte da prévia, limpa temporários e marca o repost."
---

# Fechamento do conteúdo (depois de postar)

Por que existe: ela pedia a mesma lista toda vez que um conteúdo terminava ("salva na pasta, arruma o tracker, deixa o vídeo lá"). Em nov/2026, no reel do Fies, um erro foi achado depois de postar. A fonte da prévia ainda não estava na pasta, e o tracker estava vago, sem nada sobre o conteúdo. Este skill faz tudo sem ela pedir. Vale para todas as marcas (News Brasil, EUA, OPC) e todos os formatos de reel e post.

## Quando rodar
- Logo depois que o Metricool confirmar a publicação. Conferir com getScheduledPosts (PUBLISHED, ou ERROR com aviso); nunca dizer que postou sem esse retorno.
- De novo quando ela apontar um erro num conteúdo que já está no ar (ver Correção pós-post).

## 1. Pasta do conteúdo no Drive (a mesma do ROTEIRO)
Deixar na pasta v<N>_<slug>:
- **MP4 final:** baixar a cópia do Metricool, que é pública, e subir pela Composio (GOOGLEDRIVE_UPLOAD_FILE, account priscila).
- **Capa** (jpg).
- **Fonte da prévia em zip** (<slug>_fonte_previa_v<N>.zip): HTML, data.js, scripts de build e render, áudio por cena (cru e acelerado), efeitos e música, fotos e fontes. Sem o vídeo de referência pesado e sem versões antigas. Serve pra corrigir ou repostar sem refazer do zero.
- **ROTEIRO e TRANSCRIÇÕES:** nunca apagar documento. Limpar só arquivo temporário, duplicado ou de teste, e dizer o que saiu.

## 2. NOTE final no ROTEIRO
Acrescentar um bloco "NOTE — AAAA-MM-DD (postado)" no fim, sem mexer nas notas antigas, com:
- links do post e horário;
- versão final e o que mudou;
- collabs que entraram e que falharam;
- o que ficou de fora e deve entrar num repost.

## 3. Tracker: a linha precisa contar o conteúdo, não só links
Aba da marca (News Brasil: "🇧🇷 Brazil In Production" na planilha News — Content Control, 1QFHa_xcuLOqbbYbtzeMVhb5ypfHIbAkVJyyInCKlgcM). Preencher todas as colunas da linha:
- **F Status:** "POSTADO AAAA-MM-DD (redes)". Avisos vão em Notas, não aqui.
- **H Caption:** a legenda completa.
- **J Output Link:** links do post + link do MP4 no Drive.
- **P Categoria:** tema (educação, impostos, segurança...), pra achar a pesquisa depois.
- **Q Resumo do conteúdo:** o que o vídeo conta, em 3 ou 4 frases: o gancho, a virada e a frase final.
- **R Fatos e números principais:** os dados que aparecem no vídeo, com ano.
- **S Estudos e fontes:** leis, bases de dados e estudos usados.
- **T Pessoas e partidos:** com ideologia.
- **U Ficha técnica:** duração, formato ou skill, voz e velocidade.
- **V Notas / Repost:** erros achados, o que mudar antes de repostar, a data do repost e onde está a fonte da prévia.

Se a aba de outra marca não tiver essas colunas, criar no fim da linha de cabeçalho com os mesmos nomes.

## 4. Aba "🤝 Collabs e marcações" (planilha News)
Atualizar quem aceitou, quem o Metricool não conseguiu adicionar, @ confirmados e @ errados. Os extras que não couberem como collab entram como marcação.

## 5. Repost (regras do postar-agendar)
Se o conteúdo for PERENE ou SEMANAS, criar evento no Google Calendar na data sugerida (ex.: época do tema, como o Sisu em janeiro), com:
- o que corrigir ou atualizar antes;
- links da pasta, do zip da fonte, do ROTEIRO e do post original.

## 6. Limpeza
- Apagar o branch temporário do GitHub usado pra hospedar a mídia (pela API delete-reference, pela Composio, se o git push --delete falhar).
- A prévia (artifact) fica: republicar no mesmo link com a versão final e uma nota "postado".

## 7. Resposta pra ela (curta)
Lista com:
- links do post;
- o que foi salvo e onde (pasta e quais colunas do tracker);
- collabs;
- data do repost no calendário;
- pendências que dependem dela (ex.: marcar alguém pelo app depois de publicado).

## Correção pós-post (quando acharem erro num post que já está no ar)
1. **Conferir na fonte primária** (lei na redação original e cada alteração com o ano, dado oficial) antes de concordar ou discordar. Dizer claramente o que estava errado e se havia outro erro parecido.
2. **Post no ar:** o vídeo não dá pra editar. Entregar o texto pronto de um comentário de correção pra ela fixar (curto, com a fonte).
3. **Corrigir a fonte:**
   - narração no script;
   - linhas e letra miúda no HTML;
   - republicar a prévia no mesmo link com a nota "correção pós-post".
   A voz paga só é regravada quando for repostar.
4. **Registrar:**
   - NOTE "ERRO" no ROTEIRO;
   - coluna Notas / Repost no tracker com ⚠️;
   - novo zip da fonte na pasta;
   - descrição do evento de repost atualizada.
5. Se o erro for de um tipo que pode voltar, propor ajuste no skill do formato ou no reel-pasta-roteiro-auditoria. Exemplo: atribuir a um governo uma regra que veio depois.