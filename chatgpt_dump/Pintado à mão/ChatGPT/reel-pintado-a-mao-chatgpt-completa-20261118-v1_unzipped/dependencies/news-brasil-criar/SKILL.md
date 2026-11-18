---
name: news-brasil-criar
description: Criar conteúdo News Brasil a partir de link e instrução, incluindo coolonizacao-br, investigação, documentação e prévia com áudio. Também avaliar se existe história sem produzir quando pedido.
---

# News Brasil no Codex

Leia primeiro regras-priih/SKILL.md e as quatro referências. Em nuvem, leia a cópia versionada deste pacote no GitHub e confira skills.lock.json. Nunca use oak-park-ai-hub como destino News.

Receber link + instrução + coolonizacao-br basta. Não exigir que Priih conheça dependências. Leia coolonizacao-br, coolonizacao, roteiro-storytelling, reel-pasta-roteiro-auditoria, auditoria-dissonancia, reel-zona-segura, reel-som e reel-renderizar. Use reel-editorial-guiado somente quando o formato corresponder à apresentação PLP299. Seu estilo específico não é formato universal de News.

## Dois modos
- “Só vê se tem história”, “não cria ainda”: baixar, transcrever, documentar o original, investigar fontes primárias e entregar avaliação curta com provas e limites. PARAR antes de roteiro de produção, narração, animação ou prévia.
- “Cria”, sem restrição de análise: avançar até prévia assistível. Não parar só em roteiro ou storyboard.

## Execução
1. Preserve TODAS as mensagens originais disponíveis, na ordem, no topo de ROTEIRO. Registre origem e lacunas. Resumo nunca se chama RAW integral. Feedbacks entram como acréscimos datados. Recupere chats antes de pedir repetição.
2. Localize Shared drive News > Brazil > Reels_Shorts. Crie pasta v<N>_<slug>, ROTEIRO, TRANSCRIÇÕES, resources/, png/, motion/ e linha em News Content Control. Nunca My Drive final. Upload com supportsAllDrives=True, sem create_file content=. Confirme os arquivos pelo Drive.
3. Baixe o link com ferramenta disponível ou runner de News. Use yt-dlp se disponível. Instagram pode exigir sessão; registre o erro real, preserve o link e tente a rota autorizada de nuvem. Não peça upload antes de esgotar rotas existentes. Transcreva com tempos e contexto completo; não invente trecho inacessível.
4. Investigue alegações, mecanismo causal, responsabilidade municipal/estadual/federal, projeto, autoria, tramitação e voto nominal quando houver. Perfil de todas as pessoas e fontes que opinam; estudos relevantes, datas, períodos comparáveis, fontes primárias e evidência arquivada. Atualize notícia antes de voz final, renderização e postagem.
5. Escreva história falada contínua, script palavra por palavra e mapa de batidas: trecho, tempo de palavra, visual, animação, fonte/licença e conclusão. Documente tudo em ROTEIRO. TRANSCRIÇÕES preserva o original inteiro disponível.
6. Audite fatos, fala humana, entendimento por leigos, termos técnicos explicados, causalidade, dissonância, zona segura, legibilidade, ritmo, fontes e correspondência fala/imagem. Corrija antes da entrega; versão própria da auditoria só acrescentada.
7. Monte voz grátis Andrew Multilingual ou Thalita, tempos reais por palavra, clipes pertinentes e legenda de duas linhas com palavra atual amarela. Player com play, busca, ±5/10/30s, velocidades 1/1.05/1.1/1.2/1.5/2/3x, notas abaixo das velocidades, copiar legenda/comentário e original. Use a página /reel?id=ID; atualize o dataset e assets versionados. Registre no Estúdio o mesmo link. Nada de túnel dependente do Mac como entrega móvel.
8. Teste URL HTTPS, áudio, fim, busca e cenas em 390px e 1280px. Nunca chamar algo de testado se só foi preparado. Notas e decisões precisam persistir em planilha, não apenas localStorage.
9. Pare na aprovação da prévia. MP4 só após aprovação explícita da versão atual. Voz paga só após aprovação do vídeo inteiro com voz grátis. Aprovação de uma versão anterior não libera outra. Publicar exige instrução própria.

## Regras editoriais críticas
Nunca escrever nem falar o nome do presidente atual: governo atual + lulinha desenhada. Sem falso equilíbrio, sem suavizar político. Sem travessão no texto dela. Sem menção a IA em legenda/comentário. Referências visuais não viram imagens copiadas. Preserve versões e texto existente. Se faltar uma conexão, complete o independente e consolide o que falta em uma lista só, sem expor segredos.

## Continuidade e sincronização
O repositório é a fonte versionada; mudanças de skill devem atualizar lock, pacote remoto e instalação local na mesma rodada. Rode scripts/skills_sync.py check e testes antes de declarar sincronizado. Não sobrescreva arquivo que mudou dos dois lados. A instalação local usa symlink para o mesmo checkout, evitando duas cópias locais divergentes. O celular precisa de sessão Codex na nuvem com acesso ao repositório; autocomplete local não garante disponibilidade no celular. Na ausência de autocomplete use linguagem normal e leia este arquivo remoto. Não prometer disponibilidade de ferramenta local com Mac offline.


## Preservar ideia pesquisada · regra da Priih de 17/11/2026
Modo análise termina salvando a ideia pesquisada, não descartando-a. Usar a aba já existente 🔎 Research / Content Ideas de News Content Control. Campos separados: Vídeo iniciado?, Etapa da pesquisa, Etapa da produção, Motivo do adiamento, Pasta News, Resources, Próxima ação, ID e Histórico. Vídeo não iniciado fica em pasta “(ideia de vídeo) nome do assunto”, dentro de News, com Resources e links cruzados. Créditos e prioridade só são motivos quando informados. Story found não muda o modo nem autoriza voz/produção. Retomada exige “cria” explícito e preserva a pesquisa e o histórico. Destinos só News/News Brasil/News USA, nunca OPC.


## 17/11/2026 · Entrada por área e nomes reconhecíveis
Preservar este alias News Brasil. News EUA usa news-usa-criar; a entrada conjunta é news-criar. OPC e UGC usam opc-criar e ugc-criar com seus fluxos/templates e pastas próprios; guia-criacao faz o roteamento sem misturar marcas. Assim que o assunto da peça ficar claro, dar ao chat um título com tema concreto e ângulo reconhecível. Ler antes de renomear um chat existente; não adivinhar pelo título. Manter o nome durante revisões e mudar só quando o tema mudar de verdade. Compartilhar motor, versões e contrato, não identidades editoriais. Carregar apenas as dependências relevantes; reutilizar pesquisa e assets; atualizar o Estúdio nos checkpoints, sem redeploy a cada mensagem. Economia não limita criatividade nem elimina estilos 3D quando o formato pede e a capacidade foi verificada.


## 17/11/2026 · Correção de acesso em sessões sem o Mac
Esta nota corrige os caminhos de nuvem citados acima, preservados apenas como histórico. O repositório atual das skills News é priihigashi/news, privado. NÃO procurar a skill no repositório do Painel, nem exigir que /Users/... ou ~/.agents/... existam em sessão na nuvem. A instalação local e o pacote privado salvo na conta não comprovam descoberta automática em outro produto ou chat.

Se a skill não aparecer no catálogo, ler os arquivos diretamente pelo conector GitHub usando repository_full_name=priihigashi/news e path exato. Não depender de busca ou indexação para achar arquivo conhecido:
- news-brasil-criar: news-codex/skill/news-brasil-criar/SKILL.md
- coolonizacao-br: news-codex/skill/dependencies/coolonizacao-br/SKILL.md
- regras-priih: news-codex/skill/dependencies/regras-priih/SKILL.md
- As quatro referências de regras-priih ficam em news-codex/skill/dependencies/regras-priih/references/.
- Demais dependências: news-codex/skill/dependencies/<nome>/SKILL.md.
- Lista e integridade: news-codex/skills.lock.json.

Links diretos verificáveis:
https://github.com/priihigashi/news/blob/main/news-codex/skill/news-brasil-criar/SKILL.md
https://github.com/priihigashi/news/blob/main/news-codex/skill/dependencies/coolonizacao-br/SKILL.md

Continuar o link, roteiro e feedback já presentes na conversa. Não pedir reenvio do conteúdo nem reconstruir o roteiro sem ler o existente. Se o conector GitHub não tiver acesso ao repositório privado, dizer especificamente qual acesso faltou; um caminho inexistente no Mac não prova ausência do arquivo remoto. Não prometer acesso no telefone sem testar nessa sessão.
