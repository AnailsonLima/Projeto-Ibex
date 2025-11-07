# ibex/produtos.py

from database.conexao import conectar
import os

# ============================ utilitários locais ==============================

def _pausar(msg="\nPressione Enter para continuar..."):
    input(msg)

def _limpar():
    os.system("cls" if os.name == "nt" else "clear")

def _ler_int(prompt, minimo=None, maximo=None):
    while True:
        v = input(prompt).strip()
        try:
            n = int(v)
        except:
            print("Digite um número inteiro válido.")
            continue
        if minimo is not None and n < minimo:
            print(f"Valor mínimo: {minimo}.")
            continue
        if maximo is not None and n > maximo:
            print(f"Valor máximo: {maximo}.")
            continue
        return n

def _ler_float(prompt, minimo=None, maximo=None):
    while True:
        v = input(prompt).strip().replace(",", ".")
        try:
            x = float(v)
        except:
            print("Digite um número (ex.: 19.90).")
            continue
        if minimo is not None and x < minimo:
            print(f"Valor mínimo: {minimo}.")
            continue
        if maximo is not None and x > maximo:
            print(f"Valor máximo: {maximo}.")
            continue
        return x

def _ler_texto(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Campo obrigatório.")

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
    con.commit()
    con.close()

# =============================== listagens ====================================

def listar_produtos(empresa_id=None):
    """
    Lista produtos no console.
    - Se empresa_id for None: lista TODOS (visão do cliente).
    - Se empresa_id tiver valor: lista APENAS os da empresa.
    """
    _ensure_tables()
    _limpar()
    print("=== Lista de Produtos ===")

    con = conectar()
    cur = con.cursor()
    try:
        if empresa_id is None:
            cur.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY nome;")
        else:
            cur.execute("""
                SELECT id, nome, preco, estoque
                FROM produtos
                WHERE empresa_id = ?
                ORDER BY nome;
            """, (empresa_id,))
        rows = cur.fetchall()
    finally:
        con.close()

    if not rows:
        print("Nenhum produto encontrado.")
        return []

    print(f"{'ID':>4}  {'Nome':<30} {'Preço':>10} {'Estoque':>8}")
    for pid, nome, preco, est in rows:
        print(f"{pid:>4}  {nome:<30} {preco:>10.2f} {est:>8}")
    return rows

# ================================ CRUD ========================================

def cadastrar_produto(empresa_id: int):
    _ensure_tables()
    _limpar()
    print("=== Cadastrar Produto ===")

    nome = _ler_texto("Nome: ")
    preco = _ler_float("Preço (ex.: 19.90): ", minimo=0.0)
    estoque = _ler_int("Estoque inicial: ", minimo=0)

    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT INTO produtos (empresa_id, nome, preco, estoque)
            VALUES (?, ?, ?, ?);
        """, (empresa_id, nome, preco, estoque))
        con.commit()
        print("✅ Produto cadastrado com sucesso!")
    except Exception as e:
        print("Erro ao cadastrar produto:", e)
    finally:
        con.close()
        _pausar()

def editar_produto(empresa_id: int):
    _ensure_tables()
    _limpar()
    print("=== Editar Produto ===")
    meus = listar_produtos(empresa_id)
    if not meus:
        _pausar()
        return

    pid = _ler_int("\nID do produto para editar: ", minimo=1)

    # confere se pertence à empresa
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, nome, preco, estoque FROM produtos WHERE id = ? AND empresa_id = ?;",
                (pid, empresa_id))
    row = cur.fetchone()
    if not row:
        con.close()
        print("Produto não encontrado ou não pertence a esta empresa.")
        _pausar()
        return

    _, nome_atual, preco_atual, est_atual = row
    print(f"\nDeixe vazio para manter o valor atual.")
    novo_nome = input(f"Nome [{nome_atual}]: ").strip() or nome_atual

    # preço
    v = input(f"Preço [{preco_atual:.2f}]: ").strip()
    if v == "":
        novo_preco = preco_atual
    else:
        try:
            novo_preco = float(v.replace(",", "."))
        except:
            print("Preço inválido. Mantendo valor atual.")
            novo_preco = preco_atual

    # estoque
    v = input(f"Estoque [{est_atual}]: ").strip()
    if v == "":
        novo_estoque = est_atual
    else:
        try:
            novo_estoque = int(v)
            if novo_estoque < 0:
                print("Estoque não pode ser negativo. Mantendo valor atual.")
                novo_estoque = est_atual
        except:
            print("Estoque inválido. Mantendo valor atual.")
            novo_estoque = est_atual

    try:
        cur.execute("""
            UPDATE produtos
            SET nome = ?, preco = ?, estoque = ?
            WHERE id = ? AND empresa_id = ?;
        """, (novo_nome, novo_preco, novo_estoque, pid, empresa_id))
        con.commit()
        print("✅ Produto atualizado com sucesso!")
    except Exception as e:
        print("Erro ao atualizar produto:", e)
    finally:
        con.close()
        _pausar()

def remover_produto(empresa_id: int):
    _ensure_tables()
    _limpar()
    print("=== Remover Produto ===")
    meus = listar_produtos(empresa_id)
    if not meus:
        _pausar()
        return

    pid = _ler_int("\nID do produto para remover: ", minimo=1)

    con = conectar()
    cur = con.cursor()
    # Confere se pertence à empresa
    cur.execute("SELECT nome FROM produtos WHERE id = ? AND empresa_id = ?;", (pid, empresa_id))
    row = cur.fetchone()
    if not row:
        con.close()
        print("Produto não encontrado ou não pertence a esta empresa.")
        _pausar()
        return

    nome = row[0]
    conf = input(f"Confirmar remoção de '{nome}' (S/N)? ").strip().upper()
    if conf != "S":
        print("Operação cancelada.")
        con.close()
        _pausar()
        return

    try:
        cur.execute("DELETE FROM produtos WHERE id = ? AND empresa_id = ?;", (pid, empresa_id))
        con.commit()
        print("✅ Produto removido com sucesso!")
    except Exception as e:
        print("Erro ao remover produto (verifique vínculos em pedidos):", e)
    finally:
        con.close()
        _pausar()
