# ibex/relatorios.py
# -*- coding: utf-8 -*-

"""
Relatórios do Ibex (Empresa)
- relatorio_vendas(empresa_id): consolida itens vendidos por produto, receita e quantidade
- relatorio_estoque(empresa_id): mostra estoque atual e valor total estocado (preco*estoque)
- Coerente com os schemas:
  produtos(id, empresa_id, nome, preco, estoque, criado_em)
  carrinho(..., produto_id, qtd, preco_unit, total_item, pedido_codigo, criado_em)
"""

from database.conexao import conectar
import os

# ============================ utilitários locais ==============================

def _pausar(msg="\nPressione Enter para continuar..."):
    input(msg)

def _limpar():
    os.system("cls" if os.name == "nt" else "clear")

def _moeda(v):
    try:
        return f"R$ {float(v):.2f}"
    except:
        return f"R$ {v}"

# ============================ garantias de tabelas ============================

def _ensure_tables():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL DEFAULT 0,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS carrinho (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            qtd INTEGER NOT NULL,
            preco_unit REAL NOT NULL,
            total_item REAL NOT NULL,
            cep TEXT NOT NULL,
            numero TEXT NOT NULL,
            pedido_codigo TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.commit()
    con.close()

# ================================ Relatórios ==================================

def relatorio_estoque(empresa_id: int):
    """
    Mostra estoque atual da empresa:
    - Lista produtos com (id, nome, estoque, preço, valor_total_item)
    - Soma quantidade total em estoque e valor total em R$
    """
    _ensure_tables()
    _limpar()
    print("=== Relatório de Estoque ===")

    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT id, nome, preco, estoque, (preco * estoque) AS valor_total
        FROM produtos
        WHERE empresa_id = ?
        ORDER BY nome;
    """, (empresa_id,))
    rows = cur.fetchall()

    if not rows:
        con.close()
        print("Nenhum produto cadastrado para esta empresa.")
        _pausar()
        return

    print(f"{'ID':>4}  {'Nome':<30} {'Preço':>10} {'Estoque':>8} {'Val.Est.':>12}")
    total_qtd = 0
    total_val = 0.0
    for pid, nome, preco, est, vtot in rows:
        total_qtd += int(est)
        total_val += float(vtot)
        print(f"{pid:>4}  {nome:<30} {preco:>10.2f} {est:>8} {float(vtot):>12.2f}")

    print("-" * 72)
    print(f"{'TOTAL (itens):':>44} {total_qtd:>8} {(' ' * 4)} {'TOTAL (R$):':>12} {total_val:>12.2f}")
    con.close()
    _pausar()

def relatorio_vendas(empresa_id: int):
    """
    Consolida vendas (itens finalizados) da empresa:
    - Total de pedidos que contêm itens da empresa
    - Itens vendidos por produto (qtd e receita)
    - Receita total
    """
    _ensure_tables()
    _limpar()
    print("=== Relatório de Vendas ===")

    con = conectar()
    cur = con.cursor()

    # total de pedidos únicos que têm itens da empresa
    cur.execute("""
        SELECT COUNT(DISTINCT c.pedido_codigo)
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE p.empresa_id = ?;
    """, (empresa_id,))
    total_pedidos = cur.fetchone()[0] or 0

    # agregação por produto
    cur.execute("""
        SELECT
            p.id,
            p.nome,
            SUM(c.qtd)        AS qtd_total,
            SUM(c.total_item) AS receita
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE p.empresa_id = ?
        GROUP BY p.id, p.nome
        ORDER BY receita DESC, p.nome ASC;
    """, (empresa_id,))
    por_produto = cur.fetchall()

    # receita total
    cur.execute("""
        SELECT SUM(c.total_item)
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE p.empresa_id = ?;
    """, (empresa_id,))
    receita_total = cur.fetchone()[0] or 0.0

    con.close()

    print(f"Pedidos (com itens da empresa): {total_pedidos}")
    print("\nVendas por Produto:")
    if not por_produto:
        print("Ainda não há vendas registradas para esta empresa.")
        _pausar()
        return

    print(f"{'ID':>4}  {'Nome':<30} {'Qtd Vendida':>12} {'Receita':>14}")
    for pid, nome, qtd, receita in por_produto:
        print(f"{pid:>4}  {nome:<30} {int(qtd):>12} {_moeda(receita):>14}")

    print("-" * 68)
    print(f"{'RECEITA TOTAL:':>48} {_moeda(receita_total):>14}")
    _pausar()
