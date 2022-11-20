from datetime import datetime
from io import BytesIO

import streamlit as st

from google.oauth2 import service_account
from google.cloud import storage
import pandas as pd
import datetime

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

st.title(f"Monitor Rosa - dados mensais")

source = dados_estad_mensal
all_symbols = dados_estad_mensal.estadiamento.unique()
symbols = st.multiselect("Estadiamentos", all_symbols, all_symbols)

metrics_selector = st.selectbox(
    "Selecione a métrica desejada",
    list(metrics.keys())
)


min_date = dados_estad_mensal.data.iloc[0].dt.date
max_date = dados_estad_mensal.data.iloc[-1].dt.date

min_date = datetime.date(2020,1,1)
max_date = datetime.date(2022,1,1)

a_date = st.date_input("Período", (min_date, max_date))

st.title(f"entre {a_date[0]} e {a_date[1]}")

space(1)
dataset = dados_estad_mensal[dados_estad_mensal.primeiro_estadiamento.isin(symbols)]
fig = px.line(
    dataset, 
    x='data', 
    y=metrics[metrics_selector], 
    color='estadiamento', 
    symbol="estadiamento")

# Edit the layout
fig.update_layout(yaxis_title=metrics_selector)


st.plotly_chart(fig)

space(2)

