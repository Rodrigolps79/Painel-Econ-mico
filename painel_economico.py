# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 17:47:03 2025

@author: Rodrigo
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta


# Função para buscar dados do BCB
def bcb_series(serie_id, start_date, end_date):
    url_base = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie_id}/dados?formato=json"

    start_date = datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.strptime(end_date, "%d/%m/%Y")

    all_data = []
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + timedelta(days=3652), end_date)  # 10 anos máx.
        url = f"{url_base}&dataInicial={current_start.strftime('%d/%m/%Y')}&dataFinal={current_end.strftime('%d/%m/%Y')}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data:
                all_data.extend(data)

        current_start = current_end + timedelta(days=1)

    if not all_data:
        return pd.DataFrame(columns=["data", "valor"])

    df = pd.DataFrame(all_data)
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    return df

# Dicionário com os códigos do BCB para os indicadores selecionados
indicadores_bcb = {
    "Cesta Básica": {
        "codigo": {
            "Aracaju": 7479, "Belém": 7480, "Belo Horizonte": 7481, "Brasília": 7482, 
            "Curitiba": 7483, "Florianópolis": 7484, "Fortaleza": 7485, "Goiânia": 7486, 
            "João Pessoa": 7487, "Natal": 7488, "Porto Alegre": 7489, "Recife": 7490, 
            "Rio de Janeiro": 7491, "Salvador": 7492, "São Paulo": 7493, "Vitória": 7494
        },
        "unidade": "R$"
    },
    "Índice de Emprego Formal": {
        "codigo": {
            "Total": 25239,
            "Indústria da Transformação": 25241,
            "Comércio": 25256,
            "Serviços": 25257,
            "Construção Civil": 25255
        },
        "unidade": "Índice (base 2013 = 100)"
    },
    "IPCA": {
        "codigo": 433,
        "unidade": "%"
    },
    "Taxa Selic": {
        "codigo": 4189,
        "unidade": "%"
    },
    "Câmbio": {
        "codigo": 1,
        "unidade": "R$"
    }
}

# Dicionário com unidades de medida para os indicadores
unidades_valor = {
    "IPCA": "%",
    "Taxa Selic": "%",
    "Câmbio": "R$",
    "Cesta Básica": "R$",
    "Índice de Emprego Formal": "Índice (base 2013 = 100)"
}

# Configuração da interface no Streamlit
st.markdown(
"<h3 style='text-align: center; color: #2D3E50;'>Painel Econômico</h3>"
, unsafe_allow_html=
True
)

# Sidebar
st.sidebar.header("🔎 Escolha os Indicadores")
indicador = st.sidebar.selectbox(
    "Selecione um indicador", 
    list(indicadores_bcb.keys()), 
    index=0,
    help="Escolha o indicador econômico desejado"
)

# Período de Análise com slider
datai = st.sidebar.date_input("Data inicial", datetime(2015, 1, 1))
dataf = st.sidebar.date_input("Data final", datetime.today())

# Exibir explicação sobre o indicador escolhido
st.sidebar.write(f"**{indicador}**: Exibe informações relacionadas a {indicador}")

# Lógica para selecionar os dados corretos
if indicador == "Cesta Básica":
    municipio = st.sidebar.selectbox("Selecione o município", list(indicadores_bcb[indicador]["codigo"].keys()))
    codigo_sgs = indicadores_bcb[indicador]["codigo"][municipio]
    df = bcb_series(codigo_sgs, datai.strftime("%d/%m/%Y"), dataf.strftime("%d/%m/%Y"))
    st.subheader(f"📌 Cesta Básica - {municipio}")
    unidade = unidades_valor[indicador]

elif indicador == "Índice de Emprego Formal":
    categoria = st.sidebar.selectbox("Selecione a categoria", list(indicadores_bcb[indicador]["codigo"].keys()))
    codigo_sgs = indicadores_bcb[indicador]["codigo"][categoria]
    df = bcb_series(codigo_sgs, datai.strftime("%d/%m/%Y"), dataf.strftime("%d/%m/%Y"))
    st.subheader(f"📌 Índice de Emprego Formal - {categoria}")
    unidade = unidades_valor[indicador]

else:
    # Para os outros indicadores (IPCA, Selic, Câmbio)
    codigo_sgs = indicadores_bcb[indicador]["codigo"]
    df = bcb_series(codigo_sgs, datai.strftime("%d/%m/%Y"), dataf.strftime("%d/%m/%Y"))
    st.subheader(f"📌 {indicador}")
    unidade = unidades_valor[indicador]

# Exibir unidade de medida
st.markdown(f"**Unidade de medida:** {unidade}")

# Exibir dados
if not df.empty:
    st.line_chart(df.set_index("data"))
    st.dataframe(df)
else:
    st.warning("Nenhum dado encontrado para esse período.")

# Exibir média, mediana e desvio padrão (Resumo)
if not df.empty:
    st.subheader("📊 Estatísticas Descritivas")
    st.write(f"Média: {df['valor'].mean():.2f} {unidade}")
    st.write(f"Mediana: {df['valor'].median():.2f} {unidade}")
    st.write(f"Desvio Padrão: {df['valor'].std():.2f} {unidade}")

# Fonte dos dados
st.markdown("""
    <br>
    <hr>
    <h6 style='text-align: center; font-size: 12px;'>
        Fonte: <a href="https://api.bcb.gov.br/" target="_blank">Banco Central do Brasil</a>
    </h6>
""", unsafe_allow_html=True)

st.markdown(
    "<h5 style='text-align: center;font-size: 10px;'>By Rodrigo Lopes</h5>",
    unsafe_allow_html=True
)
