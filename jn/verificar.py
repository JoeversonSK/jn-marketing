"""Testa o token e mostra o ID da conta. Uso: python -m jn.verificar"""
import os
import sys

from jn.instagram import ErroInstagram, Instagram


def main():
    try:
        ig = Instagram(os.environ.get("IG_ACCESS_TOKEN", ""), os.environ.get("IG_USER_ID") or None)
        perfil = ig.meu_perfil()
        limite = ig.limite_publicacao()
    except ErroInstagram as e:
        sys.exit(f"Não funcionou: {e}")
    print(f"Conectado como @{perfil.get('username')}")
    print(f"IG_USER_ID = {ig.ig_id}")
    print(f"Limite de publicação: {limite}")


if __name__ == "__main__":
    main()
