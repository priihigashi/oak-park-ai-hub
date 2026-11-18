# Postagem, Drive e ferramentas (News Brasil)

## Página
- Nome: "Tentando chegar até você" (@tentandochegaratevoce: Instagram, TikTok, Facebook). Página em inglês: @tryingtoreach.you (adaptar pros EUA).
- Público no Brasil: horários em horário de Brasília. Espaçar posts no mínimo 3 h. Mesmo assunto não se repete em menos de 10 posts.
- "Posta" = publicar agora. Ela não faz nada no pipeline: você renderiza, hospeda, sobe e agenda. Ela quer assistir o MP4 final uma vez antes de postar (deixar o post pronto sem horário até ela aprovar).
- Postar em Instagram + TikTok + Facebook (e YouTube Shorts quando configurado).
- Legenda de post de news começa com "COMPARTILHA NOS STORIES", recomenda criar lista de Melhores Amigos pra alcançar a família, depois o conteúdo. Evitar o nome do presidente atual e de políticos nas hashtags; evitar escrever "Trump". Nunca mencionar IA.
- 1º comentário fixado: começa com o COMENTA (ex.: "comenta o nome da sua cidade..."), linha ".", linha ".", depois poucas fontes fortes. 2º comentário ela posta manualmente.
- Collabs atuais em reels políticos: @brasilforadacaverna, @projeto.contraponto, @13mulheres, @LuzManifesto, @PortaVozLulaBR, @342artes (collab). Tags quando faltar vaga: @andrezaoliveira.pe, @brics_brasil, o político em destaque. Collab só pra contas aliadas da causa. Lista viva na aba "🤝 Collabs e marcações" da planilha News — Content Control. Trial reels: sem collab.
- Metricool: copiar o arquivo final pra pasta pública temporária "Metricool public" (Drive ID 1_i1tkJDOz0LNKsWOvcNnAmSmDhll2SQ3), agendar pelo link, depois mandar a cópia pro lixo. Links públicos no GitHub também são temporários. "Instagram: ERROR" no Metricool pode ter postado mesmo assim.
- Trial reels: pelo Metricool não dá (conta < 1K); ela posta do celular, precisa do arquivo pra baixar.
- Depois de postar (skill reel-fechamento): uma versão final só, MP4 + capa + fonte da prévia na pasta do Drive, linha do tracker preenchida com conteúdo real; erros achados depois ficam registrados; prova da fonte (print com data) salva na pasta.
- Ações que os posts pediram (consultas, PLs, e-mails): aba "🗳 Acompanhamento das ações"; revisar um mês depois.
- Links que não deu pra baixar: aba "📥 Vídeos pra baixar".

## Drive (News)
- Shared drive News. Reels Brasil: News > Brazil > Reels_Shorts > v<N>_<slug> (pasta com ROTEIRO, TRANSCRIÇÕES, resources/, png/, motion/).
- Pesquisa sobre político: pasta com o nome da pessoa dentro de News > Brazil.
- Planilha de ideias/conteúdo: "News — Content Control" (News drive), não a Ideas & Inbox.
- Fotos de políticos: News > "Políticos · Fotos" (ID 1p8NJEsfgyqdNabXwVTOWV8ZqJ__Rng64). Recortes de rosto em News > Templates (nunca apagar).
- Nunca salvar no My Drive como destino final. Upload de arquivo: OAuth Python ou Composio Workbench (upload_local_file → GOOGLEDRIVE_UPLOAD_FILE), sempre supportsAllDrives=True. NUNCA create_file com content= (cria arquivo vazio).
- Arquivos: só acrescentar/atualizar seções; nunca sobrescrever nem apagar texto existente.

## Ferramentas
- GitHub: priihigashi (repos privados). oak-park-ai-hub tem workflows: conselho.yml (auditoria ChatGPT), downloader de reels, replicate_batch.yml (secret PRI_OP_REPLICATE_API_KEY). Antes de pedir chave de API, olhe os GitHub Secrets.
- Vercel: conta priihigashi; token "claude" guardado como secret FINANCE_VERCEL em priihigashi/priscila-workspace.
- Composio: Sheets (passar `account` explicitamente; `googlesheets_allyl-rearm`), Calendar, GitHub, Outlook (Hotmail dela), Vercel.
- Metricool: marca tentandochegaratevoce.
- Tudo documentado em Drive e/ou GitHub pra que Claude e ChatGPT continuem de onde o outro parou.


## 17/11/2026 · Preservação de ideias pesquisadas
Usar a aba existente 🔎 Research / Content Ideas de News Content Control, sem criar planilha duplicada. Separar “Vídeo iniciado?”, etapa da pesquisa e etapa da produção; guardar motivo do adiamento, pasta, Resources, próxima ação, ID e histórico. Pasta de conteúdo ainda sem produção usa “(ideia de vídeo) nome do assunto”, dentro de News, com Resources contendo fontes, transcrição ou link canônico e materiais para retomar. Encontrar história não autoriza criar. Retomar lendo pesquisa e materiais existentes e somente produzir quando ela pedir criar. Não apagar o histórico quando a produção começar. A lista ganhou esses campos em K:T, em células previamente confirmadas vazias.
