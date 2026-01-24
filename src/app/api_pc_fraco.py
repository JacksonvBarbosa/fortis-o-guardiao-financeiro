import sys
import os

# =============================
# Adiciona a raiz do projeto ao path
# =============================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
import json

# =============================
# Importar módulos internos
# =============================
from src.risk_engine.fraud_detection import avaliar_fraude
from src.risk_engine.credit_risk import avaliar_credito
from src.risk_engine.financial_profile import avaliar_perfil
from src.agent.context_builder import montar_contexto_fortis

# 🔑 AGENTE PARA PC FRACO
from src.agent.ollama_agent_pc_fraco import perguntar_fortis_ollama

# =============================
# Configuração da página
# =============================
st.set_page_config(
    page_title="Fortis — Guardião Financeiro (PC Fraco)",
    layout="wide"
)

st.title("🛡️ Fortis — Guardião Financeiro")
st.caption("Modo compatível com computadores de baixo desempenho")

# =============================
# Carregar dados
# =============================
@st.cache_data
def carregar_dados():
    perfil = json.load(open("data/raw/perfil_investidor.json", encoding="utf-8"))
    transacoes = pd.read_csv("data/raw/transacoes.csv")
    movimentacoes = pd.read_csv("data/raw/movimentacoes.csv")
    return perfil, transacoes, movimentacoes

perfil_investidor_list, transacoes, movimentacoes = carregar_dados()

# =============================
# Seleção de investidor
# =============================
investidor_id = st.selectbox(
    "Selecione o investidor",
    [p["investidor_id"] for p in perfil_investidor_list]
)

perfil_investidor = next(
    p for p in perfil_investidor_list if p["investidor_id"] == investidor_id
)

# =============================
# Botão de análise
# =============================
if st.button("🔍 Analisar Situação Financeira"):
    
    # -------- 1. Avaliações de risco -------- #
    risco_fraude = avaliar_fraude(transacoes, movimentacoes)
    risco_credito = avaliar_credito(perfil_investidor, movimentacoes)
    perfil_financeiro = avaliar_perfil(transacoes, movimentacoes)

    # -------- 2. Sinais consolidados -------- #
    sinais_risco = {
        "fraude": risco_fraude["fraude_risco"],
        "credito": risco_credito["credito_risco"],
        "comportamento": perfil_financeiro["perfil_financeiro"],
        "alerta_principal": (
            risco_fraude["motivos"][0]
            if risco_fraude["motivos"]
            else "Nenhum alerta crítico identificado"
        ),
        "acao_recomendada": risco_fraude["acao_sugerida"]
    }

    # -------- 3. Resumo de transações -------- #
    resumo_transacoes = {
        "categoria_dominante": transacoes["categoria"].mode()[0],
        "media_mensal": round(transacoes["valor"].mean(), 2),
        "frequencia": "Alta" if len(transacoes) > 20 else "Moderada",
        "comportamento": perfil_financeiro["perfil_financeiro"]
    }

    # -------- 4. Resumo de movimentações -------- #
    resumo_movimentacoes = {
        "relacao": (
            "Desfavorável"
            if movimentacoes["valor"].sum() < 0
            else "Equilibrada"
        ),
        "estabilidade": perfil_financeiro["estabilidade"],
        "tendencia": (
            "Volátil"
            if movimentacoes["valor"].std() > movimentacoes["valor"].mean()
            else "Estável"
        )
    }

    # -------- 5. Montar contexto -------- #
    st.session_state.contexto = montar_contexto_fortis(
        perfil_investidor=perfil_investidor,
        resumo_transacoes=resumo_transacoes,
        resumo_movimentacoes=resumo_movimentacoes,
        sinais_risco=sinais_risco
    )

    # =============================
    # Exibição no Streamlit
    # =============================
    st.subheader("📌 Contexto enviado ao Fortis")
    st.code(st.session_state.contexto)

    st.subheader("⚠️ Sinais de Risco Identificados")
    st.json(sinais_risco)

# =============================
# Pergunta do usuário
# =============================
st.subheader("💬 Pergunte ao Fortis")

# Controle de estado
if "processando" not in st.session_state:
    st.session_state.processando = False

if "ultima_resposta" not in st.session_state:
    st.session_state.ultima_resposta = ""

with st.form(key="form_pergunta_pc_fraco", clear_on_submit=False):
    pergunta_usuario = st.text_area(
        "Digite sua pergunta aqui:",
        disabled=st.session_state.processando
    )

    enviar = st.form_submit_button(
        "Enviar pergunta",
        disabled=st.session_state.processando
    )

    if enviar:
        if "contexto" not in st.session_state:
            st.warning("⚠️ Primeiro clique em '🔍 Analisar Situação Financeira' para gerar o contexto.")

        elif not pergunta_usuario.strip():
            st.warning("⚠️ Por favor, digite uma pergunta antes de enviar.")

        else:
            st.session_state.processando = True
            st.session_state.ultima_resposta = ""

            with st.spinner("🛡️ Fortis está analisando (modo PC fraco)..."):
                resposta = perguntar_fortis_ollama(
                    pergunta_usuario,
                    st.session_state.contexto
                )
                st.session_state.ultima_resposta = resposta

            st.session_state.processando = False

# =============================
# Exibição da resposta
# =============================
if st.session_state.ultima_resposta:
    st.subheader("🤖 Resposta do Fortis")
    st.write(st.session_state.ultima_resposta)
