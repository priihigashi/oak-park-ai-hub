---
name: reel-editorial-vox
description: Criar e revisar reels editoriais em colagem animada usando o Kit Vox, incluindo capa, dados animados, tipografia e efeitos sonoros. Usar para o formato editorial da Priscila, especialmente o Reel do Congresso.
---

# Reel editorial em colagem

Preservar o original e trabalhar em uma versão identificada. Recuperar o handoff, os ativos aprovados e as correções da conversa antes de alterar a edição. Registrar o que realmente foi aplicado.

## Fonte editável é a raiz da edição

Antes de revisar um reel, localizar o projeto editável, seus ativos, a linha de tempo e o manifesto. Enquanto esse projeto existir e o vídeo não estiver aprovado, fazer **toda correção na fonte editável**: texto, números, imagens, movimento, duração e som. Renderizar o vídeo completo novamente para revisão. Usar o MP4 já renderizado somente para comparar o resultado e verificar que nenhuma correção cumulativa desapareceu.

Não transformar o MP4 exportado em projeto: não usar cortes, concatenação, congelamento de quadros, sobreposições, troca de trechos nem remux do MP4 para implementar uma revisão. Se uma correção anterior existir apenas no MP4 ou em um script de remendo, reconstruí-la primeiro na fonte e conferir o novo render completo contra a última entrega. Não declarar a fonte sincronizada sem essa conferência. Registrar no manifesto quando estiver fora de sincronia e impedir que um render temporário seja promovido como entrega.

Exceção: se a pessoa fornecer um vídeo para editar e não houver projeto editável disponível, a edição do vídeo renderizado é permitida; registrar essa condição e preservar o original. A conveniência ou a rapidez de uma correção não são exceções.

Música, efeitos, plateia e voz devem continuar em stems separados sob o mesmo relógio das cenas. Ao aumentar uma duração na fonte, recalcular eventos posteriores e gerar música contínua para a nova duração; nunca repetir ou cortar a mixagem final para preencher a pausa. Uma mudança apenas visual pode reutilizar o stem de áudio aprovado, mas não o MP4 como fonte de vídeo.

## Direção visual

Consultar [movimentos](references/movimentos.md) para linguagem, paletas e Kit Vox; [repertório](references/repertorio.md) quando precisar selecionar mecanismos de referência. Adaptar mecanismos ao tema, sem copiar capa ou sequência de uma referência.

A capa e os primeiros segundos precisam funcionar como cartaz editorial e como cena animada. Construir profundidade com arquitetura/fotografia do tema, papel ou tinta, recortes e tipografia. Usar movimentos relativos entre camadas, mudanças de escala e recortes que revelem a informação. Uma foto escurecida atrás de texto que entra não satisfaz, sozinha, esta direção.

Compor a hierarquia para celular: sujeito grande, palavras decisivas dominantes, fontes legíveis e margens reais. Textura deve ser perceptível sem prejudicar leitura. Movimentos precisam apresentar, conectar ou enfatizar informação. Evitar movimento decorativo contínuo em tudo.

## Correções aprovadas no Congresso

- Gancho: “O presidente muda. A Câmara, não.” Criar uma virada visual entre as duas partes.
- Primeira análise: desenhar a seta antes de destacar a frase; então escurecer/desfocar o entorno por um momento. Não cobrir valores, ranking ou notas.
- Manter o personagem fictício da colagem aprovada. Não substituir por desenho ou outro personagem sem solicitação. Rosto legível; imagem da arquitetura do Congresso barra a coroa acima da cabeça. Nenhuma faixa “CÂMARA” sobre o rosto.
- “REI” enorme e com entrada de impacto. Fecho “VOCÊ” também ocupa a tela.
- Após a corrida, ocultar seu gráfico para impedir que apareça entre cenas finais.
- Leis, orçamento e veto: Congresso; autorizar impeachment: Câmara. Preservar fontes e sinalizações de dados provisórios. Um handoff não substitui verificação factual quando solicitada.

## Som e entrega

Derivar os sons do mesmo relógio das animações. Marcar o quadro da chegada da palavra, contato da coroa, destaque da análise e troca de ano; alinhar o pico sonoro ao evento, compensando o ataque do efeito. Cliques dos anos seguem as trocas reais, sem metrônomo independente. Evitar efeitos genéricos acumulados que disputem com a mensagem.

Gerar uma prévia animada da abertura e um poster legível. Inspecionar quadros durante entradas, cruzamentos e saídas, além das poses finais; verificar imagens/fontes carregadas e sobreposições acidentais. Renderizar MP4 com áudio e checar decodificação e duração. Distinguir checagem técnica de avaliação auditiva: não afirmar que ouviu quando apenas conferiu tempos ou forma de onda.

Antes da entrega, comparar o render completo com a lista cumulativa de pedidos e com o último vídeo de referência; assistir e ouvir as transições relevantes e o fim. Conferir tempo real de leitura no celular. Registrar o caminho da fonte, os arquivos alterados, a duração, o áudio usado e o hash da entrega. Não apresentar como “final” um MP4 cuja fonte editável esteja desatualizada.

Entregar links para o MP4, capa e prévia, com mudanças e limitações relevantes. Não chamar uma skill de instalada apenas porque há uma cópia no projeto.

## Área segura do Instagram/TikTok (obrigatório — aprendido no Reel do Congresso, 13/10/2026)

Ao postar, o app dá zoom/corta as bordas e cobre partes da tela (barra de status, nome de usuário, legenda, convites de collab, ícones de curtir/comentar à direita). Num quadro 1080×1920:

- **Texto essencial** (título, números, frase-chave, pergunta) só dentro de **x 90–930 e y 250–1480**. Nada essencial nos 250 px do topo, nos 440 px de baixo nem nos 150 px da direita (coluna de ícones).
- **Pode ficar sob a interface:** textura, foto de fundo, partes secundárias do gráfico, rodapé de fonte pequeno — coisas que, cobertas, não mudam a mensagem.
- **Títulos de cena** (ex.: "QUEM TEM A MAIORIA?") começam em y ≥ 250, não colados no topo.
- **Arroba** dentro da área segura (y ≥ 250, à esquerda de x 900); na visão do perfil o topo é cortado.
- **Capa / grid:** palavras da capa inteiras dentro do recorte 4:5 central (y 285–1635) com ≥ 60 px de folga interna; entregar também versões 1080×1350 (4:5) e 1080×1440 (3:4) prontas para "Editar capa".
- **Conferir antes de entregar:** renderizar 1 quadro por cena com a máscara da interface (topo 250, base 440, direita 150) e verificar que nenhum texto essencial fica coberto ou cortado.
