# ibex/database/conexao.py

import os
import sqlite3

def _caminho_db():
    """
    Retorna o caminho absoluto para 'ibex.db' na raiz do projeto.
    Estrutura esperada:
    Ibex-Projeto/
      ├─ ibex/
      │   ├─ database/
      │   │   └─ conexao.py  <-- este arquivo
      │   └─ ...
      └─ ibex.db            <-- aqui ficará o banco
    """
    # __file__ -> .../ibex/database/conexao.py
    pasta_database = os.path.dirname(os.path.abspath(__file__))        # .../ibex/database
    pasta_ibex = os.path.dirname(pasta_database)                        # .../ibex
    raiz_projeto = os.path.dirname(pasta_ibex)                          # .../
    return os.path.join(raiz_projeto, "ibex.db")

def conectar():
    """
    Abre e retorna uma conexão sqlite3 já configurada.
    Uso típico:
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT 1;")
        con.close()
    """
    caminho = _caminho_db()
    # Garante que a pasta de destino exista (normalmente já existe)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    con = sqlite3.connect(caminho)
    # Opcional: acessar colunas por nome (row["coluna"])
    con.row_factory = sqlite3.Row

    # PRAGMAs úteis
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("PRAGMA journal_mode = WAL;")
    # Você pode ajustar outros PRAGMAs conforme necessidade:
    # cur.execute("PRAGMA synchronous = NORMAL;")

    con.commit()
    return con
