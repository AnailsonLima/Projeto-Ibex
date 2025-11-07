# ibex/pedidos.py

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

def _input_nonempty(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Campo obrigatório.")

# ============================ garantias de tabelas ============================

def _ensure_tables():
    """
    Garante que as tabelas mínimas existam (caso o módulo seja executado isolado).
    Mantém em sincronia com carrinho.py e produtos.
    """
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

# ============================== consultas comuns ==============================

def _listar_resumo_pedidos_cliente(cliente_id):
    """
    Retorna lista de tuplas:
    (pedido_codigo, criado_em_mais_recente, total_itens, total_valor, cep, numero)
    """
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT
            c.pedido_codigo,
            MAX(c.criado_em) AS criado_em,
            SUM(c.qtd)        AS itens,
            SUM(c.total_item) AS total,
            MAX(c.cep)        AS cep,
            MAX(c.numero)     AS numero
        FROM carrinho c
        WHERE c.cliente_id = ?
        GROUP BY c.pedido_codigo
        ORDER BY criado_em DESC;
    """, (cliente_id,))
    rows = cur.fetchall()
    con.close()
    return rows

def _listar_detalhes_pedido_cliente(cliente_id, pedido_codigo):
    """
    Retorna itens do pedido do cliente:
    (produto_id, nome, qtd, preco_unit, total_item)
    """
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT
            c.produto_id,
            p.nome,
            c.qtd,
            c.preco_unit,
            c.total_item
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.cliente_id = ? AND c.pedido_codigo = ?
        ORDER BY p.nome;
    """, (cliente_id, pedido_codigo))
    rows = cur.fetchall()
    con.close()
    return rows

def _listar_resumo_pedidos_empresa(empresa_id):
    """
    Pedidos que possuem ao menos um produto desta empresa.
    Retorna:
    (pedido_codigo, criado_em_mais_recente, total_itens_da_empresa, total_valor_da_empresa, cep, numero)
    """
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT
            c.pedido_codigo,
            MAX(c.criado_em) AS criado_em,
            SUM(c.qtd)        AS itens_empresa,
            SUM(c.total_item) AS total_empresa,
            MAX(c.cep)        AS cep,
            MAX(c.numero)     AS numero
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE p.empresa_id = ?
        GROUP BY c.pedido_codigo
        ORDER BY criado_em DESC;
    """, (empresa_id,))
    rows = cur.fetchall()
    con.close()
    return rows

def _listar_detalhes_pedido_empresa(empresa_id, pedido_codigo):
    """
    Itens do pedido que pertencem à empresa.
    Retorna:
    (produto_id, nome, qtd, preco_unit, total_item)
    """
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT
            c.produto_id,
            p.nome,
            c.qtd,
            c.preco_unit,
            c.total_item
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE p.empresa_id = ? AND c.pedido_codigo = ?
        ORDER BY p.nome;
    """, (empresa_id, pedido_codigo))
    rows = cur.fetchall()
    con.close()
    return rows

# ================================ API: Cliente ================================

def listar_pedidos_cliente(cliente_id: int):
    _ensure_tables()
    _limpar()
    print("=== Meus Pedidos ===")

    rows = _listar_resumo_pedidos_cliente(cliente_id)
    if not rows:
        print("Você ainda não possui pedidos.")
        _pausar()
        return

    print(f"{'Pedido':<22} {'Data':<20} {'Itens':>7} {'Total':>14}  Endereço")
    print("-" * 80)
    for (codigo, criado_em, itens, total, cep, numero) in rows:
        end = f"CEP {cep}, Nº {numero}"
        print(f"{codigo:<22} {criado_em:<20} {itens:>7} {(_moeda(total)):>14}  {end}")

    # opção de ver detalhes
    print("\nDigite um código de pedido para ver detalhes, ou deixe vazio para voltar.")
    escolha = input("Pedido: ").strip()
    if not escolha:
        return

    detalhes = _listar_detalhes_pedido_cliente(cliente_id, escolha)
    if not detalhes:
        print("Pedido não encontrado (ou não pertence a este cliente).")
        _pausar()
        return

    _limpar()
    print(f"=== Detalhes do Pedido {escolha} ===")
    print(f"{'Produto ID':>10}  {'Nome':<30} {'Qtd':>5} {'Preço':>10} {'Subtotal':>12}")
    total = 0.0
    for (pid, nome, qtd, preco, sub) in detalhes:
        total += float(sub)
        print(f"{pid:>10}  {nome:<30} {qtd:>5} {float(preco):>10.2f} {float(sub):>12.2f}")
    print("-" * 72)
    print(f"{'TOTAL:':>57} {total:>12.2f}")
    _pausar()

# ================================ API: Empresa ================================

def listar_pedidos_empresa(empresa_id: int):
    _ensure_tables()
    _limpar()
    print("=== Pedidos da Minha Empresa ===")

    rows = _listar_resumo_pedidos_empresa(empresa_id)
    if not rows:
        print("Ainda não há pedidos contendo produtos desta empresa.")
        _pausar()
        return

    print(f"{'Pedido':<22} {'Data':<20} {'Itens(Emp.)':>12} {'Total(Emp.)':>14}  Endereço")
    print("-" * 86)
    for (codigo, criado_em, itens_emp, total_emp, cep, numero) in rows:
        end = f"CEP {cep}, Nº {numero}"
        print(f"{codigo:<22} {criado_em:<20} {itens_emp:>12} {(_moeda(total_emp)):>14}  {end}")

    print("\nDigite um código de pedido para ver detalhes (da sua empresa), ou deixe vazio para voltar.")
    escolha = input("Pedido: ").strip()
    if not escolha:
        return

    detalhes = _listar_detalhes_pedido_empresa(empresa_id, escolha)
    if not detalhes:
        print("Pedido não encontrado ou sem itens desta empresa.")
        _pausar()
        return

    _limpar()
    print(f"=== Detalhes do Pedido {escolha} (itens da empresa) ===")
    print(f"{'Produto ID':>10}  {'Nome':<30} {'Qtd':>5} {'Preço':>10} {'Subtotal':>12}")
    total = 0.0
    for (pid, nome, qtd, preco, sub) in detalhes:
        total += float(sub)
        print(f"{pid:>10}  {nome:<30} {qtd:>5} {float(preco):>10.2f} {float(sub):>12.2f}")
    print("-" * 72)
    print(f"{'TOTAL (empresa):':>57} {total:>12.2f}")
    _pausar()
