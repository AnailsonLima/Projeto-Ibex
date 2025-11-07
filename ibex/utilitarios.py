# ibex/utilitarios.py
# -*- coding: utf-8 -*-

"""
Módulo utilitários do Ibex
- Funções genéricas e auxiliares usadas por outros módulos
- Inclui:
  - limpar tela e pausar
  - leitura segura de int/float/texto
  - validações simples (CEP, CPF, CNPJ)
  - formatação de moeda e datas
"""

import os
import re
import time
from datetime import datetime

# ========================== Limpeza e Pausa de Tela ===========================

def limpar_tela():
    """Limpa o terminal de forma compatível com Windows e Linux."""
    os.system("cls" if os.name == "nt" else "clear")

def pausar(msg="\nPressione Enter para continuar..."):
    """Pausa a execução até o usuário pressionar Enter."""
    input(msg)

# ========================== Leitura Segura de Dados ===========================

def ler_int(prompt="Número: ", minimo=None, maximo=None):
    """Lê um número inteiro validando faixas."""
    while True:
        v = input(prompt).strip()
        if not v or not v.lstrip("-").isdigit():
            print("Digite um número inteiro válido.")
            continue
        n = int(v)
        if minimo is not None and n < minimo:
            print(f"Valor mínimo: {minimo}.")
            continue
        if maximo is not None and n > maximo:
            print(f"Valor máximo: {maximo}.")
            continue
        return n

def ler_float(prompt="Valor: ", minimo=None, maximo=None):
    """Lê número decimal com validação."""
    while True:
        v = input(prompt).strip().replace(",", ".")
        try:
            n = float(v)
        except ValueError:
            print("Digite um número válido (ex.: 19.90).")
            continue
        if minimo is not None and n < minimo:
            print(f"Valor mínimo: {minimo}.")
            continue
        if maximo is not None and n > maximo:
            print(f"Valor máximo: {maximo}.")
            continue
        return n

def ler_texto(prompt="Texto: "):
    """Lê texto não vazio."""
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Campo obrigatório.")

# =============================== Validações ===================================

def validar_cep(cep: str) -> bool:
    """Valida formato de CEP (8 dígitos, com ou sem hífen)."""
    return bool(re.fullmatch(r"\d{5}-?\d{3}", cep.strip()))

def validar_cpf(cpf: str) -> bool:
    """Validação simples de CPF (11 dígitos, com ou sem pontuação)."""
    cpf = re.sub(r"\D", "", cpf)
    return len(cpf) == 11

def validar_cnpj(cnpj: str) -> bool:
    """Validação simples de CNPJ (14 dígitos)."""
    cnpj = re.sub(r"\D", "", cnpj)
    return len(cnpj) == 14

# =========================== Formatação e Data ================================

def moeda(valor):
    """Formata número como moeda (R$)."""
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)

def data_agora(fmt="%d/%m/%Y %H:%M:%S"):
    """Retorna a data/hora atual formatada."""
    return datetime.now().strftime(fmt)

def aguarde(segundos=1, msg="Processando"):
    """Mostra animação simples de espera."""
    for i in range(segundos):
        print(f"{msg}{'.' * (i % 3 + 1)}", end="\r")
        time.sleep(1)
    print(" " * 30, end="\r")

# ============================= Limpeza de Strings =============================

def apenas_digitos(txt: str) -> str:
    """Remove tudo que não for número."""
    return re.sub(r"\D", "", txt or "")

def normalizar_email(email: str) -> str:
    """Converte email para minúsculo e remove espaços extras."""
    return email.strip().lower()
