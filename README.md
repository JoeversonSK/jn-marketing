# JN Higienização — Marketing automático no Instagram

Sistema que publica sozinho no **@jn_.higienizacao** os posts, carrosséis, Reels e stories que você aprovou, e toda segunda gera um relatório de crescimento.

Ele roda no **GitHub Actions**, de graça e 24h por dia, sem precisar do seu computador ligado. As imagens ficam no **GitHub Pages**, porque a API do Instagram só aceita mídia num link público.

```
Claude cria a semana  ->  pasta conteudo/  ->  você aprova  ->  robô publica na hora marcada  ->  publicado/
                                                                     |
                                                       relatório toda segunda em relatorios/
```

O sistema só cuida do marketing: não responde Direct nem comentários.

---

## Instalação (uma vez só, cerca de 30 minutos)

### 1. Conferir o Instagram
A conta precisa ser **profissional** (Empresa ou Criador de conteúdo) e **pública**. A @jn_.higienizacao já é profissional.

### 2. Criar o aplicativo na Meta e pegar o token (feito em 06/11/2026)
- App **JN Marketing** (ID 1431217198999169), ligado ao portfólio empresarial **JN HIGIENIZAÇÃO**.
- Apps novos usam o **API setup with Unified login**: Instagram → API setup with Unified login.
- Passo 1: configuração "API do Instagram (Início de sessão unificado)" selecionada (token de usuário do sistema, **não vence**).
- Passo 2: conta **@jn_.higienizacao** (ID **17841447491627225**) adicionada como Instagram Tester → **Generate token**.

O app pode ficar em modo de desenvolvimento: para publicar na própria conta não precisa de análise da Meta.

### 3. Subir esta pasta para o GitHub
1. Crie uma conta em <https://github.com>, se ainda não tiver.
2. Instale o **GitHub Desktop**, clique em **File → Add local repository**, escolha esta pasta e clique em **Publish repository**.
3. Nome: `jn-marketing`. **Desmarque "Keep this code private"**, porque o GitHub Pages grátis só funciona em repositório público. Só ficam visíveis as artes e legendas, nunca o token.

### 4. Guardar o token como segredo
No repositório, abra **Settings → Secrets and variables → Actions → New repository secret**:

| Nome | Valor |
| --- | --- |
| `IG_ACCESS_TOKEN` | o token do passo 2 |
| `IG_USER_ID` | `17841447491627225` |

### 5. Ligar o GitHub Pages
**Settings → Pages → Source: Deploy from a branch → Branch: `main` / `(root)` → Save.**

### 6. Renovação automática do token (só para token que começa com "IG")
O token do login unificado não vence, então este passo pode ser pulado.

1. Abra <https://github.com/settings/personal-access-tokens/new>.
2. Em **Repository access**, escolha **Only select repositories → jn-marketing**.
3. Em **Permissions → Repository permissions → Secrets**, marque **Read and write**.
4. Escolha a validade máxima, gere e copie.
5. Salve como um novo segredo do repositório chamado `GH_PAT`.

### 7. Testar
Em **Actions → Publicar no Instagram → Run workflow**, rode o robô na hora. Se o log mostrar "0 item(ns) pronto(s)", está tudo certo.

---

## Uso no dia a dia

### Ver o que está programado
Abra o arquivo **`FILA.md`** no GitHub, que funciona até pelo celular. Ele mostra a prévia, o horário e a situação de cada post.

### Aprovar
Pelo GitHub, abra `conteudo/<pasta do post>/post.json`, clique no lápis, troque `"aprovado": false` por `"aprovado": true` e clique em **Commit changes**.

Pelo computador, aprove tudo de uma vez:
```
python -m jn.aprovar todos
```
Depois envie as mudanças pelo GitHub Desktop (**Commit** e **Push**).

### Adicionar um post à mão
```
pip install -r requirements.txt
python -m jn.novo_post --tipo post --quando "2026-11-13 19:00" --legenda legenda.txt arte.png
python -m jn.novo_post --tipo carrossel --quando "2026-11-11 19:00" --legenda legenda.txt 1.png 2.png 3.png
python -m jn.novo_post --tipo story --quando "2026-11-10 09:00" story.png
python -m jn.novo_post --tipo reel --quando "2026-11-09 12:00" --legenda legenda.txt video.mp4 --capa capa.png
```
As imagens são convertidas para JPG em 1080x1350 (feed) ou 1080x1920 (story e Reel).

### Formato do `post.json`
```json
{
  "tipo": "post",
  "publicar_em": "2026-11-13T19:00:00-03:00",
  "legenda": "Texto do post com #hashtags",
  "arquivos": ["01.jpg"],
  "aprovado": false
}
```
`tipo` pode ser `post`, `carrossel` (2 a 10 arquivos), `reel` (1 vídeo .mp4, com `"capa"` opcional) ou `story`.

### Se algo der errado
- O erro aparece no `FILA.md`. Depois de 3 tentativas, o post fica marcado como **falhou** e não tenta mais.
- Para tentar de novo, apague as linhas `"falhou"`, `"tentativas"` e `"ultimo_erro"` do `post.json`.
- O limite da Meta é de 100 publicações por dia pela API, bem acima do que vamos usar.

---

## Arquivos

| Arquivo | O que faz |
| --- | --- |
| `jn/publicar.py` | Publica o que está aprovado e no horário (roda de hora em hora) |
| `jn/relatorio.py` | Relatório semanal em `relatorios/` |
| `jn/renovar_token.py` | Renova o token do Instagram |
| `jn/novo_post.py` | Adiciona um post à fila |
| `jn/aprovar.py` | Aprova posts |
| `jn/verificar.py` | Testa o token: `python -m jn.verificar` |
| `jn/painel.py` | Atualiza o `FILA.md` |
| `.github/workflows/` | Os horários automáticos |

Para testar no computador, crie as variáveis de ambiente `IG_ACCESS_TOKEN` e `MIDIA_BASE_URL` (`https://SEU-USUARIO.github.io/jn-marketing`). Com `python -m jn.publicar --simular`, o sistema mostra o que publicaria, sem publicar nada.
