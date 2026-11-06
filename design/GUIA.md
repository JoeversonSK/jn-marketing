# JN Higienização: guia de marca

Este guia vale para todas as peças do Instagram (@jn_.higienizacao): feed, carrossel, stories e Reels.
Os templates em `templates/` já seguem estas regras. Use-os em vez de montar arte do zero.

## 1. Essência

**Limpo, confiável e perto de você.** A JN entra na casa do cliente, então a comunicação precisa passar segurança, frescor e organização.
O visual tem muito respiro, tipografia forte, azul profundo e formas de água desenhadas à mão (bolhas e gotas).

## 2. Logo

| Arquivo | Uso |
|---|---|
| `logo.svg` | Assinatura completa (símbolo + HIGIENIZAÇÃO) sobre fundo claro |
| `logo-branco.svg` | Assinatura completa sobre fundo azul-noite ou royal |
| `logo-simbolo.svg` | Só o círculo "JN": avatar, selo de canto, marca d'água |

- São SVGs 100% vetoriais: o texto foi convertido em contorno, então não dependem de fonte instalada. Para regenerar, rode `python3 design/tools/gerar_logo.py`.
- Área de proteção: ao redor do logo, deixe livre no mínimo **metade do diâmetro do círculo**.
- Tamanho mínimo: símbolo com 64 px num canvas de 1080 px.
- Não distorça, não gire, não aplique sombra nem contorno, não troque as cores e não coloque o logo sobre foto.

## 3. Paleta

| Token | Hex | Papel |
|---|---|---|
| `--noite` | `#0B1650` | Fundo principal das peças de campanha e texto sobre fundo claro |
| `--royal` | `#1C3AC4` | Cor da marca: fundos, selos de ícone, blobs de destaque |
| `--royal-claro` | `#2C4FDB` | Só para a onda interna do logo |
| `--noite-2` | `#12207A` | Blobs de fundo sobre azul-noite (contraste sutil) |
| `--agua` | `#5EC8F2` | Acento: palavra-chave, ícones de linha, bolhas |
| `--agua-clara` | `#78C8FF` | Acento sobre fundo royal |
| `--branco` | `#FFFFFF` | Texto sobre fundo escuro e cartões |
| `--gelo` | `#EEF3FF` | Fundo claro (peças educativas e enquetes) |
| `--limao` | `#D6F84C` | **Destaque único:** preço, oferta e botão de ação. Nunca use como texto sobre fundo claro |

**Proporção sugerida por peça:** 60% fundo (noite, royal ou gelo), 25% texto, 10% água e 5% limão.
Use **um** elemento limão por peça (ou dois quando forem oferta + botão). Se tudo é destaque, nada é destaque.

Temas prontos (classe no `.canvas`): `tema-noite` (campanha/oferta), `tema-royal` (agenda, capas), `tema-gelo` (educativo, enquete).

## 4. Tipografia

As fontes ficam em `fonts/` e são carregadas localmente (licença OFL). Nada vem de CDN.

| Estilo | Fonte | Tamanho (canvas 1080) | Detalhes |
|---|---|---|---|
| Display | Poppins Bold | 170–210 px | entrelinha 0.9, espaçamento −3,5% |
| Título | Poppins Bold | 96–136 px (**mínimo 90**) | entrelinha 1.02, espaçamento −2,5% |
| Número/oferta | Poppins Bold | 220–600 px | "%" a 50% e "OFF" a 30% do tamanho |
| Corpo | Inter Regular/Medium | 40–46 px (**mínimo 38**) | entrelinha 1.34 |
| Rótulo (sobretítulo) | Inter SemiBold, MAIÚSCULAS | 30 px | espaçamento +14%, cor de acento |
| Assinatura/rodapé | Inter SemiBold | 30 px | só @ e cidades. Não é texto de leitura |

- Os títulos ficam em caixa alta e baixa ("Chegamos."), nunca em CAIXA ALTA inteira.
- Destaque uma ou duas palavras por título com a cor de acento (`*palavra*` nos templates).
- Ponto-final colorido em títulos curtos ("Chegamos**.**") é assinatura da marca.
- Evite palavra sozinha na última linha: use `~` (espaço inseparável) nos textos dos templates.

## 5. Grid e margens

- Margem lateral: **80 px**. Feed (1080×1350): margem superior e inferior de 80 px.
- **Stories (1080×1920):** conteúdo só entre **y = 250 e y = 1670**. As faixas de cima e de baixo ficam para a interface do Instagram e recebem apenas fundo e decoração.
- **Reels:** conteúdo entre y = 290 e y = 1590. A legenda e os botões do app cobrem a parte de baixo e a lateral direita.
- **Capa de Reel:** o texto fica no miolo 4:5 (y 285 a 1635), que é o recorte exibido no perfil.
- Gutter: 24 px. Espaçamentos em múltiplos de 8 px.
- Alinhamento **sempre à esquerda**. Não centralize blocos de texto. A assimetria vem do texto à esquerda e dos blobs e bolhas à direita ou sangrando pela borda.

## 6. Hierarquia de uma peça

1. **Um** foco: título display **ou** número da oferta.
2. Uma frase de apoio (corpo).
3. Informação de serviço (itens, horário).
4. Ação: botão limão (CTA) com seta.
5. Assinatura: símbolo + "JN Higienização" no topo, @ e cidades no rodapé.

Teste: com a imagem reduzida a 25% (tamanho do celular no feed), o foco e o CTA precisam continuar legíveis.

## 7. Elementos gráficos

- **Blobs orgânicos** (`JN.formaBlob`): manchas de água geradas com curvas suaves. Use 1 ou 2 por peça, de preferência sangrando pela borda.
- **Bolhas** (`JN.bolha`): contorno fino com reflexo em arco. Use em grupos de 2 ou 3 (uma grande, uma pequena e um ponto cheio), nunca espalhadas.
- **Selo de ícone** (`JN.seloIcone`): ícone de linha dentro de um blob royal.
- **Ícones de linha próprios** (`JN.icone`): sofa, colchao, cadeira, poltrona, tapete, gota, acaro, mancha, odor, encardido, calendario, relogio, check, camera, chat, seta, local, brilho, casa, pergunta. Grade de 64 px, traço arredondado.
- Nenhum elemento decorativo pode encostar em texto. Deixe pelo menos 24 px de distância.

## 8. Tom de voz

- Próximo, direto e confiável, como um vizinho caprichoso que entende do assunto. Trate o cliente por "você".
- Fale do benefício concreto: "tira a sujeira que a limpeza do dia a dia não alcança".
- Sem promessas que não dá para provar ("elimina 100% das bactérias", "o melhor do Cariri").
- Seja específico no que for verificável: cidades, dias e horários, itens atendidos, condição da oferta.
- Todo post termina com o CTA: **orçamento por foto no Direct ou WhatsApp**.
- No máximo 3 emojis por legenda e de 5 a 8 hashtags do conjunto: #higienizacaodeestofados #juazeirodonorte #barbalha #cariri #limpezadesofa #higienizacaodecolchao #juazeirodonortece #caririce.

## 9. Nunca faça

- Degradê azul com texto centralizado e gotas translúcidas de clip-art (o visual antigo).
- Fotos de pessoas, fotos de banco de imagem ou imagens de terceiros.
- "Antes e depois" que não seja de um serviço real da JN, com autorização do cliente.
- Depoimentos inventados, números de clientes inventados, vagas "quase esgotadas" sem ser verdade.
- Logos de outras marcas, incluindo os ícones oficiais de WhatsApp e Instagram. Escreva "WhatsApp" e "@" por extenso.
- Mais de 2 fontes, texto de corpo abaixo de 38 px, título abaixo de 90 px.
- Limão como cor de texto sobre fundo claro, ou mais de um bloco limão competindo.
- Texto nas zonas de interface dos stories e Reels.

## 10. Checklist antes de entregar

- [ ] Abri a imagem final em tamanho real e reduzida (celular). Título e CTA estão legíveis?
- [ ] Os acentos (ç, ã, õ, é, á) renderizaram certo? Nenhuma letra cortada?
- [ ] `render.py` terminou sem avisos (texto cortado, fora da área, zona do story)?
- [ ] Há um único foco visual e um único CTA?
- [ ] As margens de 80 px e o alinhamento à esquerda foram respeitados? A decoração não encosta em texto?
- [ ] A assinatura (símbolo no topo, @ no rodapé) está presente?
- [ ] As informações estão corretas: oferta (20% OFF, 10 primeiros), cidades, dias e horários?
- [ ] A legenda está pronta, com no máximo 3 emojis, o CTA de orçamento por foto e de 5 a 8 hashtags?
- [ ] Reel: 12 a 20 s, 1080×1920, H.264 yuv420p e capa com o texto dentro do recorte 4:5? Conferi 4 ou 5 quadros extraídos?
- [ ] Story: a área para sticker (enquete, link) ficou livre?

## 11. Como usar o sistema

```bash
# peças estáticas (JPG q92 4:4:4) a partir de um JSON
python3 design/render.py design/exemplos/campanha-inauguracao.json --saida /caminho/saida

# Reel MP4 (30 fps, H.264, sem áudio) + capa JPG
python3 design/reel.py design/exemplos/reel-conheca.json --saida /caminho/saida
```

Templates disponíveis (os campos estão documentados no topo de cada HTML):

| Template | Formato | Para quê |
|---|---|---|
| `feed-oferta` | 1080×1350 | Capa de oferta/lançamento |
| `carrossel-capa` | 1080×1350 | Capa de carrossel educativo (número gigante) |
| `carrossel-item` | 1080×1350 | Miolo numerado (um tópico por card, com barra de progresso) |
| `carrossel-cta` | 1080×1350 | Fechamento com oferta e CTA |
| `dica` | 1080×1350 | Card de dica avulsa |
| `story-oferta` | 1080×1920 | Story de campanha |
| `story-agenda` | 1080×1920 | Agenda/vagas do dia |
| `story-enquete` | 1080×1920 | Pergunta com área livre para sticker |
| `reel-cena` | 1080×1920 | Cenas animadas: capa, gancho, problema, solucao, oferta, cta |

Para ver um template, abra o HTML no navegador: ele mostra os dados de exemplo.
Marcação nos textos: `*acento*`, `_limão_`, `\n` (quebra de linha), `~` (espaço inseparável).
