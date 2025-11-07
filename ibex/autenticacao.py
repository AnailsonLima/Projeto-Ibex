# ibex/autenticacao.py

from database.conexao import conectar
import re

# ============================ Utils locais simples ============================

def _input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Valor não pode ser vazio.")

def _normaliza_email(email: str) -> str:
    return email.strip().lower()

def _so_digitos(txt: str) -> str:
    return re.sub(r"\D", "", txt or "")

def _valida_cnpj_basico(cnpj: str) -> bool:
    # Validação simples (tamanho). Mantemos próximo ao original: sem cálculo de dígitos.
    return len(_so_digitos(cnpj)) == 14

# =============================== Infra/DB ====================================

def _criar_tabelas_se_nao_existirem():
    """
    Mantém o projeto rodável mesmo em base limpa.
    Ajuste os campos conforme seu schema original, se necessário.
    """
    con = conectar()
    cur = con.cursor()

    # Tabela de clientes (simples)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tabela de empresas (simples)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razao_social TEXT NOT NULL,
            cnpj TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    con.commit()
    con.close()

def _email_existe(tabela: str, email: str) -> bool:
    con = conectar()
    cur = con.cursor()
    cur.execute(f"SELECT 1 FROM {tabela} WHERE email = ? LIMIT 1;", (email,))
    existe = cur.fetchone() is not None
    con.close()
    return existe

def _cnpj_existe(cnpj: str) -> bool:
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT 1 FROM empresas WHERE cnpj = ? LIMIT 1;", (cnpj,))
    existe = cur.fetchone() is not None
    con.close()
    return existe

# =========================== Fluxo do CLIENTE =================================

def cadastro_cliente():
    """
    Cadastro interativo de cliente. Em caso de sucesso, retorna (id, nome).
    Caso contrário, retorna None. Mantém a experiência de terminal.
    """
    _criar_tabelas_se_nao_existirem()

    print("\n=== Cadastro de Cliente ===")
    nome = _input_nonempty("Nome: ")
    email = _normaliza_email(_input_nonempty("Email: "))
    if _email_existe("clientes", email):
        print("⚠ Já existe um cliente com este email.")
        return None

    senha = _input_nonempty("Senha: ")
    conf  = _input_nonempty("Confirme a senha: ")
    if senha != conf:
        print("⚠ Senhas não conferem.")
        return None

    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT INTO clientes (nome, email, senha)
            VALUES (?, ?, ?);
        """, (nome, email, senha))
        con.commit()
        cliente_id = cur.lastrowid
        print(f"✅ Cliente cadastrado com sucesso! ID: {cliente_id}")
        return (cliente_id, nome)
    except Exception as e:
        print(f"Erro ao cadastrar cliente: {e}")
        return None
    finally:
        con.close()

def login_cliente():
    """
    Login interativo de cliente. Retorna (id, nome) em caso de sucesso; senão None.
    """
    _criar_tabelas_se_nao_existirem()

    print("\n=== Login de Cliente ===")
    email = _normaliza_email(_input_nonempty("Email: "))
    senha = _input_nonempty("Senha: ")

    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT id, nome FROM clientes
            WHERE email = ? AND senha = ?
            LIMIT 1;
        """, (email, senha))
        row = cur.fetchone()
        if row:
            print(f"✅ Login bem-sucedido. Bem-vindo(a), {row[1]}!")
            return (row[0], row[1])
        print("⚠ Credenciais inválidas.")
        return None
    except Exception as e:
        print(f"Erro no login: {e}")
        return None
    finally:
        con.close()

def logout_cliente(sessao: dict):
    """
    Sai da sessão de cliente. Mantém formato de sessão usado no menus.py.
    """
    if sessao.get("cliente_id"):
        nome = sessao.get("cliente_nome") or sessao["cliente_id"]
        sessao["cliente_id"] = None
        sessao["cliente_nome"] = None
        print(f"✅ Cliente '{nome}' saiu da sessão.")
    else:
        print("Nenhum cliente logado.")

# =========================== Fluxo da EMPRESA =================================

def cadastro_empresa():
    """
    Cadastro interativo de empresa. Em caso de sucesso, retorna (id, razao_social).
    Caso contrário, retorna None.
    """
    _criar_tabelas_se_nao_existirem()

    print("\n=== Cadastro de Empresa ===")
    razao = _input_nonempty("Razão social: ")
    cnpj  = _so_digitos(_input_nonempty("CNPJ (apenas números ou com máscara): "))
    if not _valida_cnpj_basico(cnpj):
        print("⚠ CNPJ inválido (esperado 14 dígitos).")
        return None
    if _cnpj_existe(cnpj):
        print("⚠ Já existe uma empresa com este CNPJ.")
        return None

    email = _normaliza_email(_input_nonempty("Email: "))
    if _email_existe("empresas", email):
        print("⚠ Já existe uma empresa com este email.")
        return None

    senha = _input_nonempty("Senha: ")
    conf  = _input_nonempty("Confirme a senha: ")
    if senha != conf:
        print("⚠ Senhas não conferem.")
        return None

    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("""
            INSERT INTO empresas (razao_social, cnpj, email, senha)
            VALUES (?, ?, ?, ?);
        """, (razao, cnpj, email, senha))
        con.commit()
        empresa_id = cur.lastrowid
        print(f"✅ Empresa cadastrada com sucesso! ID: {empresa_id}")
        return (empresa_id, razao)
    except Exception as e:
        print(f"Erro ao cadastrar empresa: {e}")
        return None
    finally:
        con.close()

def login_empresa():
    """
    Login interativo de empresa. Retorna (id, razao_social) em caso de sucesso; senão None.
    """
    _criar_tabelas_se_nao_existirem()

    print("\n=== Login de Empresa ===")
    email = _normaliza_email(_input_nonempty("Email: "))
    senha = _input_nonempty("Senha: ")

    con = conectar()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT id, razao_social FROM empresas
            WHERE email = ? AND senha = ?
            LIMIT 1;
        """, (email, senha))
        row = cur.fetchone()
        if row:
            print(f"✅ Login bem-sucedido. Bem-vindo(a), {row[1]}!")
            return (row[0], row[1])
        print("⚠ Credenciais inválidas.")
        return None
    except Exception as e:
        print(f"Erro no login: {e}")
        return None
    finally:
        con.close()

def logout_empresa(sessao: dict):
    """
    Sai da sessão de empresa. Mantém formato de sessão usado no menus.py.
    """
    if sessao.get("empresa_id"):
        nome = sessao.get("empresa_nome") or sessao["empresa_id"]
        sessao["empresa_id"] = None
        sessao["empresa_nome"] = None
        print(f"✅ Empresa '{nome}' saiu da sessão.")
    else:
        print("Nenhuma empresa logada.")
