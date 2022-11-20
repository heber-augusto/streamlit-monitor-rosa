from datetime import datetime
from io import BytesIO

import streamlit as st

from google.oauth2 import service_account
from google.cloud import storage
import pandas as pd

import plotly.express as px

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)


# Retrieve file contents.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
# @st.experimental_memo(ttl=600)
def read_file(bucket_name, file_path):
    bucket = client.bucket(bucket_name)
    content = bucket.blob(file_path).download_as_bytes()
    
    bytes_io = BytesIO(content)
    dados_estad_mensal = pd.read_parquet(bytes_io)    

    dados_estad_mensal['data'] = pd.to_datetime(
        dados_estad_mensal['data'],
        format='%Y%m')
    # renomeia coluna
    dados_estad_mensal['estadiamento'] = dados_estad_mensal['primeiro_estadiamento']
    
    # remove dados de estadiamento vazio
    dados_estad_mensal = dados_estad_mensal[dados_estad_mensal.estadiamento != '']
    return dados_estad_mensal

bucket_name = "observatorio-oncologia"
file_path = r"monitor/SP/consolidado/dados_estad_mensal.parquet.gzip"

dados_estad_mensal = read_file(bucket_name, file_path)

def space(num_lines=1):
    """Adds empty lines to the Streamlit app."""
    for _ in range(num_lines):
        st.write("")

metrics = {
 'Número de pacientes': 'numero_pacientes',   
 'Óbitos':'obtitos',
 'Custo':'custo_estadiamento'
}
        
   
st.set_page_config(
    layout="wide", 
    page_icon="📈", 
    page_title="Monitor Rosa")

# Data visualisation part

sidebar = st.sidebar
metrics_selector = sidebar.selectbox(
    "Selecione a métrica desejada",
    list(metrics.keys())
)

st.title(f"Monitor Rosa - dados mensais de {metrics_selector}")

source = dados_estad_mensal
all_symbols = dados_estad_mensal.estadiamento.unique()
symbols = st.multiselect("Escolha os estadiamentos", all_symbols, all_symbols[:3])

space(1)
dataset = dados_estad_mensal[dados_estad_mensal.primeiro_estadiamento.isin(symbols)]
fig = px.line(
    dataset, 
    x='data', 
    y='numero_pacientes', 
    color='estadiamento', 
    symbol="estadiamento")

# Edit the layout
fig.update_layout(yaxis_title=metrics_selector)


st.plotly_chart(fig)

space(2)

