---
name: "reel-3d-historinha"
description: "Animações 3D (Three.js) para reels de histórias, causos e explicações, com políticos em terno 3D e cabeça real. Use quando Priih pedir história, historinha, animação, bonequinhos, cena 3D ou 3D; antes de começar, pergunte se é 2D ou 3D."
---

# Reel 3D de historinha (Three.js)

> **Antes de roteirizar, e já no primeiro vídeo de referência:** seguir também o skill reel-pasta-roteiro-auditoria (pasta v<N>_<slug>, TRANSCRIÇÕES com cada vídeo numerado, linha no tracker com a coluna Categoria preenchida, LISTA DE FEEDBACK DA PRIIH no topo do ROTEIRO, roteiro em tabela narração | animação de cada frase, conexões entre blocos, prompt de auditoria). Ele vale junto com este skill.

## Passo 0: 2D ou 3D?
Quando o pedido for uma história, historinha, causo ou envolver bonequinhos, pergunte uma vez (AskUserQuestion): **3D** (esta skill) ou **2D**? 3D custa mais tempo de construção e de render, então não é o padrão para todo conteúdo.
Opções 2D já testadas (mesma cena do limao, 30/10/2026):
- **Limpo** (skill reel-motion-limpo): fundo claro, formas chapadas, molas, texto subindo por máscara, inundação de cor. A preferida da Priih entre as 2D.
- **Colagem** (direção "Mesa de montagem" do repo extreme-motion-design, MIT): recortes de papel girados 2 a 6 graus, fita, serifa editorial (Fraunces + Hanken Grotesk), movimento em 12 quadros por segundo. Ela achou "muito colagem".
- **Explicador Vox** (skill vox-explainer do repo motion-graphics-skills, MIT): papel rasgado, retícula, letra condensada em caixa alta (Anton), marca-texto amarelo, cartões entrando em profundidade. Ela achou abaixo do esperado.

## Personagens: quem é quem (ler antes de criar qualquer boneco)
Por que existe: os bonecos prontos do KayKit Adventurers (cavaleiro, bárbaro, mago, Rogue de capuz) saem com cara de Robin Hood medieval. A Priih rejeitou no reel das bets (nov/2026) e pediu de novo o boneco de terno que ela já tinha aprovado.
- **Político ou pessoa real = terno + cabeça real, desde a 1ª versão.** Corpo de terno montado no próprio Three.js: paletó escuro (#1F2A44), camisa branca, gravata na cor do lado (vermelha esquerda, azul royal direita), calça e sapato escuros, materiais lisos (MeshPhysical, sem flatShading, geometrias com bastante segmento e bevel leve). Braços num grupo com ombro e cotovelo, pra apontar, acenar ou segurar algo. A cabeça é a foto real recortada (só a cabeça, contorno branco grosso, leve balanço do template) num plano que sempre olha pra câmera, encostada na gola, sem vão.
- **Referência aprovada:** o boneco 2D de corpo inteiro do reel "Cadê a canetada?" (v10, nov/2026: cabeça real no colarinho, terno, braço que aponta, gravata na cor do lado). O 3D copia essa leitura, só com volume e luz.
- **Pessoa anônima** (eleitor, mãe, garimpeiro): o mesmo corpo em roupa comum, ou as figurinhas que ela gera no ChatGPT. Nunca os bonecos de aventureiro em conteúdo de notícia.
- **KayKit Adventurers:** só se ela pedir algo de fantasia ou de jogo.
- Antes de animar, mostrar 1 quadro parado do personagem pra ela aprovar.
- Reaproveitar corpos de terno, poses e animações entre vídeos (guardar no kit), em vez de montar do zero.
- Ângulo e movimento combinam com a foto da cabeça: com foto de frente, o corpo fica de frente ou de três quartos; nunca girar o corpo de perfil com a cabeça frontal.

## Stack 3D (testado e aprovado como "depois")
- Three.js 0.170 via importmap do cdn.jsdelivr.net/npm (three, three/addons/, three/examples/jsm/, postprocessing@6.39.5/build/index.js, n8ao@2.0.1/dist/N8AO.js).
- Bonecos prontos e animados (só para fantasia/jogo, ver Personagens): **KayKit Adventurers** (Kay Lousberg, CC0, uso livre comercial), no GitHub KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0, pasta addons/kaykit_character_pack_adventures/Characters/gltf/ (Barbarian, Knight, Mage, Rogue, Rogue_Hooded; ~3,6 MB cada, 76 animações: Idle, Walking_A/B/C, Running_A, Cheer, Interact, PickUp, Sit_Chair_*, Lie_*, Hit_A, Jump_*, Throw, Use_Item...). Baixar com git sparse/clone sem checkout + `git checkout HEAD -- <arquivo>`. Esconder armas: nós com knife|crossbow|throwable (e Rogue_Cape se quiser). Outras fontes CC0: Quaternius, Kenney (sites costumam estar bloqueados na nuvem; preferir cópias no GitHub). O RobotExpressive do repo do three.js (CC0) também baixa por raw.githubusercontent.com.
- O artifact não serve .glb: converter para base64 num arquivo `rogue.js` (`window.ROGUE_B64="..."`), carregar com `<script src>` e usar `GLTFLoader().parseAsync(bytes.buffer,'')`. Publicar com publish_files (index.html + .js).
- Clonar o boneco por cena com `SkeletonUtils.clone`; animação determinística (serve pro seek e pro render): `mixer.stopAllAction(); mixer.clipAction(clip).play()` ao trocar e `mixer.setTime(t)` a cada quadro. Escalar pela bounding box (altura ~2,75).
- Efeitos "suco no rosto" e afins: esfera MeshPhysical translúcida presa à posição do osso `head`.

## Luz e acabamento (o que fez a diferença)
- `ACESFilmicToneMapping`, exposure ~0,82; ambiente `RoomEnvironment` via PMREM com `environmentIntensity` ~0,22; sol 1,7 com sombra PCF 2048 e `shadow.radius` 5, `normalBias` 0,02; luz de recorte na cor tema; hemisférica baixa (0,18).
- Materiais lisos (sem flatShading), mais segmentos nas geometrias, bevel leve; janelas/lâmpadas com emissive para o brilho pegar.
- Pós-processamento (EffectComposer com render target HalfFloat samples 4): RenderPass -> **N8AOPass** (aoRadius 1,4, distanceFalloff 1,2, intensity 3,2, quality High, **`configuration.gammaCorrection = false`**, senão fica tudo lavado por gamma duplo) -> UnrealBloomPass (0,22 / 0,4 / limiar 0,95) -> BokehPass (focus = distância câmera-alvo, aperture 0,0035, maxblur 0,008) -> OutputPass por último.
- Fog leve só ao fundo (16 a 34). Textos de placas/papéis com MeshBasicMaterial `toneMapped:false`.
- Referência de API e erros comuns: skill threejs-skills (CloudAI-X, MIT), arquivos threejs-postprocessing e threejs-lighting.
- Para o MP4 final, opcional: three-gpu-pathtracer dá luz fisicamente real, mas é lento; só vale no render quadro a quadro, testar num quadro antes.

## Motor e preview
- Palco lógico 1080x1920 com UI em DOM escalada; cenas como grupos com janela [a,b) de tempo e update(t) puro (nada de estado entre quadros), câmera por cena com lerp + easing, elementos entram na palavra falada.
- Teste local: Playwright com `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`, servir a pasta por http.server (fetch de file:// falha), redirecionar os CDNs para node_modules (npm funciona).
- Seguir todas as regras de reel da Priih (legenda 2 linhas, palavra atual na cor tema, ZONA SEGURA do skill reel-zona-segura: texto em x 150-915 e y 268-1680, cena 3D pode ir até a borda, conferir com moldura de Story e Reel antes do MP4; fonte na base, banner de 0:50, preview com velocidades, notas, legenda do post e primeiro comentário, voz grátis no rascunho, MP4 só após aprovação).
- Gastar pouco: testar um trecho curto (~10 s) antes de construir o vídeo todo; sem agentes paralelos a menos que ela peça.

## Quando o HTML não der conta: trecho no Blender (decisão dela, 4/nov/2026)
- Todo 3D começa em HTML (Three.js), com prévia ao vivo no celular e funcionando com o Mac desligado.
- Não buscar realismo por padrão. Blender só quando a melhoria ajudar a explicar o assunto ou resolver uma limitação visual relevante, e só depois de tentar corrigir no HTML a iluminação, os materiais, a proporção e o movimento.
- Mesmo aí, só aquele trecho vai pro Blender. Precisa do Mac dela ligado com o Blender e a conexão MCP do Blender instalados (conferir antes; se não tiver, avisar e propor a instalação).
- Pra economizar: testar primeiro uma amostra curta do trecho mais difícil; antes de renderizar, ela aprova composição, câmera, ação e duração (1 ou 2 quadros parados).
- Legendas, títulos, chips e fontes continuam em HTML por cima do vídeo, pra corrigir texto sem renderizar de novo.
- O render entra na mesma prévia como vídeo no lugar da cena, sincronizado com o áudio principal, funcionando com play, pausa, busca e velocidades. Só na prévia, uma etiqueta no canto: "BLENDER · mudar cena = novo render" (não vai pro MP4).
- Mudar a cena do Blender custa um render novo: juntar todas as correções dela antes. Mudar os textos por cima não custa render.