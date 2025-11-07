# ibex/menus.py
# ========= Utilitários básicos (limpar tela, pausar, leitura segura) =========
try:
    from utilitarios import limpar_tela, pausar, ler_int
except Exception:
    
    import os
    def limpar_tela():
        os.system("cls" if os.name == "nt" else "clear")

    def pausar(msg="\nPressione Enter para continuar..."):
        input(msg)

    def ler_int(prompt="Opção: "):
        while True:
            val = input(prompt).strip()
            if val.isdigit():
                return int(val)
            print("Digite um número válido.")


# --- Autenticação ---
try:
    from autenticacao import (
        login_cliente, cadastro_cliente, logout_cliente,
        login_empresa, cadastro_empresa, logout_empresa
    )
except Exception:
    def login_cliente(): print("TODO: login_cliente()"); return None
    def cadastro_cliente(): print("TODO: cadastro_cliente()"); return None
    def logout_cliente(sessao): print("TODO: logout_cliente()")
    def login_empresa(): print("TODO: login_empresa()"); return None
    def cadastro_empresa(): print("TODO: cadastro_empresa()"); return None
    def logout_empresa(sessao): print("TODO: logout_empresa()")

# --- Produtos ---
try:
    from produtos import (
        listar_produtos, cadastrar_produto, editar_produto, remover_produto
    )
except Exception:
    def listar_produtos(): print("TODO: listar_produtos()")
    def cadastrar_produto(empresa_id): print("TODO: cadastrar_produto()")
    def editar_produto(empresa_id): print("TODO: editar_produto()")
    def remover_produto(empresa_id): print("TODO: remover_produto()")


try:
    from carrinho import (
        adicionar_ao_carrinho, remover_do_carrinho, ver_carrinho, finalizar_pedido
    )
except Exception:
    def adicionar_ao_carrinho(cliente_id): print("TODO: adicionar_ao_carrinho()")
    def remover_do_carrinho(cliente_id): print("TODO: remover_do_carrinho()")
    def ver_carrinho(cliente_id): print("TODO: ver_carrinho()")
    def finalizar_pedido(cliente_id):
        print("TODO: finalizar_pedido() (versão fiel ao original)")

try:
    from pedidos import listar_pedidos_cliente, listar_pedidos_empresa
except Exception:
    def listar_pedidos_cliente(cliente_id): print("TODO: listar_pedidos_cliente()")
    def listar_pedidos_empresa(empresa_id): print("TODO: listar_pedidos_empresa()")

# --- Relatórios (Sistema) ---
try:
    from relatorio import relatorio_vendas, relatorio_estoque
except Exception:
    def relatorio_vendas(empresa_id): print("TODO: relatorio_vendas()")
    def relatorio_estoque(empresa_id): print("TODO: relatorio_estoque()")

# ============================== Estado de Sessão ==============================
# Mantém quem está logado (cliente ou empresa). Use exatamente um por vez.
SESSAO = {
    "cliente_id": None,
    "empresa_id": None,
    "cliente_nome": None,  
    "empresa_nome": None,  
}

def _precisa_cliente():
    if SESSAO["cliente_id"] is None:
        print("⚠ É necessário estar logado como CLIENTE para essa ação.")
        pausar()
        return False
    return True

def _precisa_empresa():
    if SESSAO["empresa_id"] is None:
        print("⚠ É necessário estar logado como EMPRESA para essa ação.")
        pausar()
        return False
    return True

# ================================ Menus =======================================

def menu_principal():
    while True:
        limpar_tela()
        print("===================================")
        print("        🧱 IBEX - Principal")
        print("===================================")
        _mostra_status_sessao()
        print("\n1. Área do Cliente")
        print("2. Área da Empresa")
        print("0. Sair")

        op = ler_int("\nEscolha: ")

        if op == 1:
            menu_cliente()
        elif op == 2:
            menu_empresa()
        elif op == 0:
            print("Saindo do Ibex...")
            break
        else:
            print("Opção inválida!")
            pausar()


def _mostra_status_sessao():
    if SESSAO["cliente_id"]:
        print(f"👤 Cliente logado: {SESSAO['cliente_nome'] or SESSAO['cliente_id']}")
    elif SESSAO["empresa_id"]:
        print(f"🏢 Empresa logada: {SESSAO['empresa_nome'] or SESSAO['empresa_id']}")
    else:
        print("🔓 Ninguém logado")

# ------------------------------- Área do Cliente ------------------------------

def menu_cliente():
    while True:
        limpar_tela()
        print("============= Área do Cliente =============")
        _mostra_status_sessao()
        print("\n1. Login de Cliente")
        print("2. Cadastro de Cliente")
        print("3. Listar Produtos")
        print("4. Adicionar ao Carrinho")
        print("5. Ver Carrinho")
        print("6. Remover do Carrinho")
        print("7. Finalizar Pedido (fiel ao original)")
        print("8. Meus Pedidos")
        print("9. Logout do Cliente")
        print("0. Voltar")

        op = ler_int("\nEscolha: ")

        if op == 1:
            
            res = login_cliente()
            if res:
                SESSAO["cliente_id"], SESSAO["cliente_nome"] = res[0], (res[1] if len(res) > 1 else None)
                SESSAO["empresa_id"], SESSAO["empresa_nome"] = None, None  # força exclusividade
            pausar()

        elif op == 2:
            cadastro_cliente()
            pausar()

        elif op == 3:
            listar_produtos()
            pausar()

        elif op == 4:
            if _precisa_cliente():
                adicionar_ao_carrinho(SESSAO["cliente_id"])
                pausar()

        elif op == 5:
            if _precisa_cliente():
                ver_carrinho(SESSAO["cliente_id"])
                pausar()

        elif op == 6:
            if _precisa_cliente():
                remover_do_carrinho(SESSAO["cliente_id"])
                pausar()

        elif op == 7:
            if _precisa_cliente():
                finalizar_pedido(SESSAO["cliente_id"])
                pausar()

        elif op == 8:
            if _precisa_cliente():
                listar_pedidos_cliente(SESSAO["cliente_id"])
                pausar()

        elif op == 9:
            if SESSAO["cliente_id"]:
                logout_cliente(SESSAO)
            else:
                print("Nenhum cliente logado.")
            pausar()

        elif op == 0:
            break
        else:
            print("Opção inválida!")
            pausar()

# ------------------------------- Área da Empresa ------------------------------

def menu_empresa():
    while True:
        limpar_tela()
        print("============= Área da Empresa =============")
        _mostra_status_sessao()
        print("\n1. Login de Empresa")
        print("2. Cadastro de Empresa")
        print("3. Cadastrar Produto")
        print("4. Editar Produto")
        print("5. Remover Produto")
        print("6. Relatório de Vendas")
        print("7. Relatório de Estoque")
        print("8. Pedidos da Minha Empresa")
        print("9. Logout da Empresa")
        print("0. Voltar")

        op = ler_int("\nEscolha: ")

        if op == 1:
            res = login_empresa()
            if res:
                SESSAO["empresa_id"], SESSAO["empresa_nome"] = res[0], (res[1] if len(res) > 1 else None)
                SESSAO["cliente_id"], SESSAO["cliente_nome"] = None, None  # força exclusividade
            pausar()

        elif op == 2:
            cadastro_empresa()
            pausar()

        elif op == 3:
            if _precisa_empresa():
                cadastrar_produto(SESSAO["empresa_id"])
                pausar()

        elif op == 4:
            if _precisa_empresa():
                editar_produto(SESSAO["empresa_id"])
                pausar()

        elif op == 5:
            if _precisa_empresa():
                remover_produto(SESSAO["empresa_id"])
                pausar()

        elif op == 6:
            if _precisa_empresa():
                relatorio_vendas(SESSAO["empresa_id"])
                pausar()

        elif op == 7:
            if _precisa_empresa():
                relatorio_estoque(SESSAO["empresa_id"])
                pausar()

        elif op == 8:
            if _precisa_empresa():
                listar_pedidos_empresa(SESSAO["empresa_id"])
                pausar()

        elif op == 9:
            if SESSAO["empresa_id"]:
                logout_empresa(SESSAO)
            else:
                print("Nenhuma empresa logada.")
            pausar()

        elif op == 0:
            break
        else:
            print("Opção inválida!")
            pausar()
