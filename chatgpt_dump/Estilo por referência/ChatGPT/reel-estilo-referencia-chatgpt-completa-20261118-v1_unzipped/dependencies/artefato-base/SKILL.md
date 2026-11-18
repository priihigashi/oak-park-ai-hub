---
name: artefato-base
description: Base de estrutura de TODA página interativa que o Claude cria pra Priih (painéis, hubs, sites como o OBSERVA, trackers, apps de aprovação, prévias com menu). Use antes de criar ou mudar qualquer artefato ou site com navegação, botões ou cartões. Crava o TEMPLATE antes de começar e encaixa coisa nova pelo modelo do tipo dela. Referência de estrutura (não de cor) o "Tinder de Conteúdo" https://claude.ai/artifact/PwL5Q633NCvkqLPrWtm1gb. Não vale pros vídeos dos reels.
---

# Artefato base da Priih

Ela reclamou dos artefatos novos: "template muito zoado", menu e botões ruins, "fica pondo tips". Disse que a estrutura do "Tinder de Conteúdo" (https://claude.ai/artifact/PwL5Q633NCvkqLPrWtm1gb, hoje na pasta Arquivados, mas fica como referência) é melhor que muitos artefatos, sem dizer que ama ele, e não gostou do roxo com preto. Ela sempre aponta o site do ADHD como inspiração de design. Antes de criar, abra o Tinder (e o site do ADHD, se tiver o link) e siga a estrutura, não invente outra.

## Regras que não mudam

1. **Nada de caixa de "tip", "dica", "nota", "💡 como usar" na tela.** Se uma explicação é necessária, ela vira um texto curto e apagado (cor muted) embaixo do título, uma linha só. Instrução longa vai pra um botão "?" que abre um bottom sheet.
2. **Uma ação principal por tela**, grande, embaixo, fácil de tocar com o dedão. Ações secundárias são menores e mais apagadas.
3. **Mobile primeiro** (ela lê no iPhone), mas no computador as colunas abrem lado a lado.
4. **Menu = barra fixa no topo + abas em pílula** (segmented control). Nada de menu lateral com 10 itens, nada de botões soltos espalhados.
5. **Cada coisa num cartão.** Cartão de vidro com borda fina, cantos bem arredondados, espaço de sobra dentro.
6. **Estado vazio sempre desenhado** (ícone, uma frase, um botão), nunca uma área em branco.
7. **Sem texto pequeno demais.** Mínimo 12 px pra texto lido; título de cartão 18 px+, peso 800.
8. **Fontes**: moderna, bold, levemente arredondada (regra dela). Padrão: a fonte do sistema da Apple (-apple-system, "SF Pro Display") como no Tinder; se precisar de Google Font, Nunito ou Figtree. Alternar pesos (800 nos títulos, 600 nos rótulos, 400 no corpo).
9. **Dado que precisa durar não fica só no navegador.** localStorage só pra conveniência (aba aberta, rascunho). Notas, favoritos e decisões dela vão pra planilha ou pro banco do artefato, senão somem no celular.
10. **Antes de entregar**: screenshot no tamanho de celular (390 px) e de computador (1280 px). Conferir menu, botões, quebras de linha, nada cortado.

## Cores: o Tinder é modelo de ESTRUTURA, não de cor

Ela disse: "eu nem tô falando que eu gosto desse do Tinder, só que tá melhor do que muitos dos artefatos... não gostei muito da cor roxa e preto." Então copie do Tinder a estrutura (barra, abas, cartões, botões, bottom sheet, estados vazios, animações), NÃO a paleta. Não usar roxo com fundo preto.

A paleta oficial ainda vai ser escolhida com ela (inspiração: o site do ADHD que ela sempre cita). Até lá: fundo claro e limpo (dark mode opcional pelo sistema), cartões brancos com borda fina, UMA cor de destaque por conta (OPC amarelo #CBCC10; News a cor do dia; o resto escolhe uma e mantém em todas as telas daquele site). Quando ela aprovar a paleta, troque a seção abaixo.

Referência de como o Tinder declara os tokens (só o formato, as cores vão mudar):

```css
:root {
  --bg: #0b0b14;
  --glass: rgba(255,255,255,0.06);
  --glass-border: rgba(255,255,255,0.12);
  --glass-hover: rgba(255,255,255,0.10);
  --pink: #f472b6;  --pink2: #ec4899;  --pink-dim: rgba(244,114,182,0.15);
  --purple: #a78bfa; --purple-dim: rgba(167,139,250,0.15);
  --green: #34d399;  --red: #f87171;  --amber: #fbbf24;
  --text: #f1f0fa;
  --muted: rgba(241,240,250,0.45);
  --muted2: rgba(241,240,250,0.25);
  --grad: linear-gradient(135deg, #f472b6, #a78bfa);
}
body { background: var(--bg); color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif; }
/* brilho suave no fundo */
body::before { content:''; position:fixed; top:-30%; left:50%; transform:translateX(-50%);
  width:600px; height:600px; pointer-events:none; z-index:0;
  background: radial-gradient(circle, rgba(244,114,182,.12) 0%, rgba(167,139,250,.08) 50%, transparent 70%); }
```

A cor de destaque (rosa e lilás) pode trocar por conta: OPC usa o amarelo #CBCC10 no lugar do rosa; News segue a cor do dia. A estrutura não troca.

## Peças (copiar do Tinder)

- **Barra do topo**: sticky, fundo `rgba(11,11,20,.85)` com `backdrop-filter: blur(20px)`, borda de baixo fina. Título à esquerda em gradiente (800, ~17 px). À direita, uma pílula de seleção (conta, nicho, período) que abre um bottom sheet.
- **Abas**: pílula de vidro com padding 3 px; cada aba `flex:1`, 13 px, 600; a ativa com gradiente rosa→lilás a 30% e borda rosa. Emoji curto antes do nome (📁 🔥 📦).
- **Contador e barra de progresso**: linha de 3 px em gradiente + "<strong>12</strong> restando de <strong>35</strong>" pequeno e centralizado.
- **Cartão**: gradiente de vidro 145°, borda `--glass-border`, `border-radius: 22px`, padding 22 px, sombra `0 8px 40px rgba(0,0,0,.4)` + brilho interno no topo (linha de 1 px em gradiente). Dentro: data em caixa alta pequena e apagada; chip da série (pílula rosa-dim); título 18 px 800; slug/código em monoespaçada pequena; link como pílula lilás-dim.
- **Botões de ação**: dupla embaixo do cartão. Secundário (Não/Skip) `flex:1`, vermelho-dim. Principal (Sim/Trabalhar) `flex:2`, gradiente a 25%, 800. `border-radius: 16px`, padding 15 px, `scale(1.02)` no hover e `scale(.97)` no toque.
- **Bottom sheet** (no lugar de modal no meio da tela): sobe de baixo com alça de 36×4 px, fundo escuro em gradiente, cantos 24 px em cima, animação `slideUp .22s cubic-bezier(.34,1.56,.64,1)`. Botão principal em gradiente cheio, "Fechar" em vidro.
- **Lista simples** (arquivados, histórico): linhas de vidro com 10 px de raio, título apagado, ação pequena em lilás à direita.
- **Estado vazio**: emoji grande, título 16 px 700, uma frase apagada, botão de vidro.
- **Animação**: cartão sai girando pro lado (Sim pra direita, Não pra esquerda), 0,3 s. Atalhos de teclado ← → e Esc.

## Cravar a estrutura ANTES de começar (e nunca "no feeling")

Reclamação dela: "você nunca crava a estrutura antes de começar um site. E quando vai incluir uma coisa nova, você não usa do template... cada hora adicionava como bem entendia, no feeling." O OBSERVA nasceu nesse mesmo estilo, estava bom e está ficando bagunçado por isso.

1. **Todo site ou painel novo começa por um TEMPLATE escrito**, antes de qualquer conteúdo: um bloco `/* TEMPLATE */` no topo do CSS (ou um arquivo DESIGN.md no repo do site) com:
   - a página: barra do topo, abas, largura máxima, grade;
   - os níveis de título (H1, H2, H3: tamanho, peso, cor) e o título de categoria (texto em negrito, sem fundo, com espaço antes: "aqui começa a categoria tal");
   - **um modelo por TIPO de bloco**, com nome: cartão de informação, cartão de ação (Sim/Não), calculadora, gráfico, lista, tabela, alerta, estado vazio. Cada tipo tem SEMPRE a mesma cor, o mesmo fundo e o mesmo lugar dos botões (ex.: toda calculadora = fundo mais escuro que o cartão normal, borda lilás, campos à esquerda e resultado grande à direita);
   - as cores de cada categoria ou conta.
2. **Coisa nova entra pelo modelo do tipo dela.** Pediram uma calculadora nova? Copia o modelo "calculadora". Não existe modelo pra esse tipo? Primeiro cria o modelo e anota no TEMPLATE, depois usa. Nunca um bloco desenhado do zero no meio da página.
3. **Mudança de visual muda o TEMPLATE**, e o template muda todos os blocos daquele tipo de uma vez. Nada de consertar um bloco só e deixar os outros diferentes.
4. **Página lotada ganha submenu**, não mais um bloco embaixo do outro.
5. Antes de entregar, passe a página inteira e confira: todo bloco é de um tipo do TEMPLATE? Algum ficou "diferente sem motivo"? Conserta antes de mostrar.

## Painéis com várias colunas (hub, Painel da Manhã)

Mesmos cartões e cores. No computador: grade de 3 colunas (esquerda números fixos, meio o que fazer hoje com o cartão principal em destaque, direita coluna que fecha com "fechar ›"). No celular: tudo empilhado, primeiro o que precisa dela. Caixas que abrem ao clicar = cartões com chevron que expandem no lugar.

## Checklist antes de publicar

- [ ] O TEMPLATE do site está escrito e todo bloco é de um tipo dele.
- [ ] Abri o Tinder de Conteúdo e o meu tem a mesma lógica de barra, abas, cartões e botões (sem roxo com preto).
- [ ] Nenhuma caixa de dica ou tutorial na tela.
- [ ] Uma ação principal por tela, grande e embaixo.
- [ ] Screenshot em 390 px e em 1280 px, nada cortado, nenhuma linha com 1 ou 2 palavras.
- [ ] O que ela decide ou anota fica salvo fora do navegador.
