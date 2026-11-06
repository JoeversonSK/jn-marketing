#!/usr/bin/env bash
# Salva no repositório o que o robô mudou (posts publicados, tentativas) sem brigar com
# aprovações feitas pelo app ao mesmo tempo. FILA.md é sempre regerado, nunca mesclado.
set -u
git config user.name "jn-robo"
git config user.email "jn-robo@users.noreply.github.com"
git checkout -- FILA.md 2>/dev/null || true
git add -A conteudo
[ -d publicado ] && git add -A publicado
git diff --cached --quiet || git commit -q -m "Robô: fila atualizada"
for i in 1 2 3 4 5; do
  git pull -q --rebase -X theirs origin main || { git rebase --abort 2>/dev/null; sleep 3; continue; }
  python -m jn.painel
  git add FILA.md
  git diff --cached --quiet || git commit -q -m "Robô: FILA.md"
  git push -q origin HEAD:main && exit 0
  sleep 5
done
echo "::warning::Não consegui salvar a fila depois de 5 tentativas."
exit 0
