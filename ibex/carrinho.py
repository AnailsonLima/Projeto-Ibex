# ibex/carrinho.py

from database.conexao import conectar
import datetime
import os

# ============================ utilitários locais ==============================

def _pausar(msg="\nPressione Enter para continuar..."):
    input(msg)

def _limpar():
    os.system("cls" if os.name == "nt" else "clear")

def _input_int(prompt, minimo=None, maximo=None):
    while True:
        v = input(prompt).strip()
        if not v.isdigit():
            print("Digite um número válido.")
            continue
        v = int(v)
        if minimo is not None and v < minimo:
            print(f"Valor mínimo: {minimo}")
            continue
        if maximo is not None and v > maximo:
            print(f"Valor máximo: {maximo}")
            continue
        return v

def _input_nonempty(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Campo obrigatório.")

# ============================ criação de tabelas ==============================

def _ensure_tables():
    con = conectar()
    cur = con.cursor()

    # produtos (mínimo necessário para o carrinho)
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

    # carrinho_temp: rascunho por cliente
    cur.execute("""
        CREATE TABLE IF NOT EXISTS carrinho_temp (
            cliente_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            qtd INTEGER NOT NULL,
            UNIQUE (cliente_id, produto_id)
        );
    """)

    # carrinho: destino final (cada item finalizado vira uma linha)
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

# ============================== helpers de produtos ===========================

def _get_produto(produto_id):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ?;", (produto_id,))
    row = cur.fetchone()
    con.close()
    return row  # (id, nome, preco, estoque) ou None

def _listar_produtos_console():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY id;")
    rows = cur.fetchall()
    con.close()

    if not rows:
        print("Não há produtos cadastrados.")
        return []

    print("\n=== Produtos Disponíveis ===")
    print(f"{'ID':>4}  {'Nome':<30} {'Preço':>10} {'Estoque':>8}")
    for (pid, nome, preco, est) in rows:
        print(f"{pid:>4}  {nome:<30} {preco:>10.2f} {est:>8}")
    return rows

# =============================== API do menu =================================

def adicionar_ao_carrinho(cliente_id: int):
    _ensure_tables()
    _limpar()
    print("=== Adicionar ao Carrinho ===")
    rows = _listar_produtos_console()
    if not rows:
        _pausar()
        return

    produto_id = _input_int("\nDigite o ID do produto: ", minimo=1)
    prod = _get_produto(produto_id)
    if not prod:
        print("Produto não encontrado.")
        _pausar()
        return

    _, nome, _, estoque = prod
    if estoque <= 0:
        print(f"Produto '{nome}' sem estoque.")
        _pausar()
        return

    qtd = _input_int(f"Quantidade (estoque atual: {estoque}): ", minimo=1)
    if qtd > estoque:
        print("Quantidade solicitada maior que o estoque disponível.")
        _pausar()
        return

    con = conectar()
    cur = con.cursor()
    try:
        # se já existir no temp, soma
        cur.execute("""
            INSERT INTO carrinho_temp (cliente_id, produto_id, qtd)
            VALUES (?, ?, ?)
            ON CONFLICT(cliente_id, produto_id) DO UPDATE SET
                qtd = qtd + excluded.qtd;
        """, (cliente_id, produto_id, qtd))
        con.commit()
        print(f"✅ '{nome}' (x{qtd}) adicionado ao carrinho.")
    except Exception as e:
        print("Erro ao adicionar:", e)
    finally:
        con.close()

def ver_carrinho(cliente_id: int):
    _ensure_tables()
    _limpar()
    print("=== Meu Carrinho (rascunho) ===")

    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT ct.produto_id, p.nome, p.preco, ct.qtd, (p.preco * ct.qtd) as subtotal
        FROM carrinho_temp ct
        JOIN produtos p ON p.id = ct.produto_id
        WHERE ct.cliente_id = ?
        ORDER BY p.nome;
    """, (cliente_id,))
    rows = cur.fetchall()
    con.close()

    if not rows:
        print("Seu carrinho está vazio.")
        return

    total = 0.0
    print(f"{'ID':>4}  {'Nome':<30} {'Preço':>10} {'Qtd':>5} {'Subtotal':>12}")
    for pid, nome, preco, qtd, sub in rows:
        total += float(sub)
        print(f"{pid:>4}  {nome:<30} {preco:>10.2f} {qtd:>5} {sub:>12.2f}")
    print("-" * 66)
    print(f"{'TOTAL:':>53} {total:>12.2f}")

def remover_do_carrinho(cliente_id: int):
    _ensure_tables()
    _limpar()
    print("=== Remover do Carrinho ===")
    ver_carrinho(cliente_id)

    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT produto_id, qtd FROM carrinho_temp WHERE cliente_id = ?;", (cliente_id,))
    itens = {pid: qtd for pid, qtd in cur.fetchall()}
    if not itens:
        _pausar()
        con.close()
        return

    produto_id = _input_int("\nID do produto para remover/diminuir: ", minimo=1)
    if produto_id not in itens:
        print("Produto não está no carrinho.")
        _pausar()
        con.close()
        return

    qtd_atual = itens[produto_id]
    print(f"Quantidade atual desse item no carrinho: {qtd_atual}")
    qtd_remover = _input_int("Quantidade a remover (mín. 1): ", minimo=1)

    try:
        if qtd_remover >= qtd_atual:
            cur.execute("DELETE FROM carrinho_temp WHERE cliente_id = ? AND produto_id = ?;",
                        (cliente_id, produto_id))
            print("Item removido do carrinho.")
        else:
            cur.execute("""
                UPDATE carrinho_temp SET qtd = qtd - ?
                WHERE cliente_id = ? AND produto_id = ?;
            """, (qtd_remover, cliente_id, produto_id))
            print("Quantidade atualizada.")
        con.commit()
    except Exception as e:
        print("Erro ao remover:", e)
    finally:
        con.close()
        _pausar()

def finalizar_pedido(cliente_id: int):
    """
    FIEL AO ORIGINAL (espírito): interativo, pede CEP e número, confirma,
    grava em 'carrinho' e só então baixa o estoque e limpa o carrinho_temp.
    Cada item final vira uma linha na tabela 'carrinho' com 'pedido_codigo'
    para agrupar.
    """
    _ensure_tables()
    _limpar()
    print("=== Finalizar Pedido ===")

    # Lê carrinho_temp
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT ct.produto_id, p.nome, p.preco, p.estoque, ct.qtd, (p.preco * ct.qtd) as subtotal
        FROM carrinho_temp ct
        JOIN produtos p ON p.id = ct.produto_id
        WHERE ct.cliente_id = ?
        ORDER BY p.nome;
    """, (cliente_id,))
    itens = cur.fetchall()
    if not itens:
        print("Seu carrinho está vazio.")
        con.close()
        _pausar()
        return

    # Mostra resumo
    total = 0.0
    print(f"{'ID':>4}  {'Nome':<30} {'Preço':>10} {'Qtd':>5} {'Subtotal':>12} {'Estoque':>9}")
    for pid, nome, preco, est, qtd, sub in itens:
        total += float(sub)
        print(f"{pid:>4}  {nome:<30} {preco:>10.2f} {qtd:>5} {sub:>12.2f} {est:>9}")
    print("-" * 74)
    print(f"{'TOTAL:':>61} {total:>12.2f}")

    # Coleta endereço (como no original, via terminal)
    cep = _input_nonempty("\nCEP (apenas números ou com máscara): ")
    numero = _input_nonempty("Número: ")

    # Confirmação
    conf = input("\nConfirmar pedido? (S/N): ").strip().upper()
    if conf != "S":
        print("Operação cancelada.")
        con.close()
        _pausar()
        return

    # Validação de estoque atual antes de confirmar (pode ter mudado)
    for pid, nome, preco, est, qtd, _ in itens:
        if qtd > est:
            print(f"⚠ Estoque insuficiente para '{nome}'. Disponível: {est}, solicitado: {qtd}.")
            con.close()
            _pausar()
            return

    # Gerar um código de pedido simples para agrupar linhas na tabela 'carrinho'
    pedido_codigo = f"P{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{cliente_id}"

    try:
        # Transação
        cur.execute("BEGIN;")

        # Inserir cada item no 'carrinho' final
        for pid, nome, preco, est, qtd, sub in itens:
            cur.execute("""
                INSERT INTO carrinho
                (cliente_id, produto_id, qtd, preco_unit, total_item, cep, numero, pedido_codigo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (cliente_id, pid, qtd, float(preco), float(preco) * qtd, cep, numero, pedido_codigo))

            # Baixar estoque do produto
            cur.execute("""
                UPDATE produtos SET estoque = estoque - ?
                WHERE id = ?;
            """, (qtd, pid))

        # Limpar carrinho_temp do cliente
        cur.execute("DELETE FROM carrinho_temp WHERE cliente_id = ?;", (cliente_id,))

        con.commit()

        print("\n✅ Pedido confirmado com sucesso!")
        print(f"Código do pedido: {pedido_codigo}")
        print(f"Itens: {len(itens)} | Total: R$ {total:.2f}")
        print("Endereço:", f"CEP {cep}, Nº {numero}")

    except Exception as e:
        con.rollback()
        print("Erro ao finalizar pedido:", e)
    finally:
        con.close()
        _pausar()
