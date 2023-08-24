from datetime import datetime
from io import BytesIO

import streamlit as st

from google.oauth2 import service_account
from google.cloud import storage
import pandas as pd
import datetime

import plotly.express as px


st.set_page_config(
    layout="wide", 
    page_icon="📈", 
    page_title="Monitor Rosa")


# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)


metrics = {
 'Número de pacientes em tratamento': 'numero_pacientes',   
 'Óbitos':'obitos',
 'Custo':'custo_estadiamento',
 'Custo por paciente': 'custo_por_paciente',
 'Número de diagnosticos': 'numero_diagnosticos'      
}
 


# Retrieve file contents.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=3600)
def read_file(bucket_name, final_parquet_folder):
    bucket = client.bucket(bucket_name)

    # Lista os blobs no bucket
    blobs = bucket.list_blobs(prefix=final_parquet_folder)
    for blob in blobs:
        if blob.name.endswith(".parquet"):
            file_path = blob.name
            break
    
    content = bucket.blob(file_path).download_as_bytes()
    
    bytes_io = BytesIO(content)
    dados_estad_mensal = pd.read_parquet(bytes_io)    

    dados_estad_mensal['data'] = pd.to_datetime(
        dados_estad_mensal['data'],
        format='%Y%m')
    # renomeia coluna
    dados_estad_mensal['estadiamento'] = dados_estad_mensal['primeiro_estadiamento']
    
    # remove dados de estadiamento vazio
    dados_estad_mensal = dados_estad_mensal[(dados_estad_mensal.estadiamento != '') & (dados_estad_mensal.estado == 'São Paulo')]
    dados_estad_mensal['custo_por_paciente'] = dados_estad_mensal['custo_estadiamento'] / dados_estad_mensal['numero_pacientes']
    
    
    # cria média móvel para cada uma das colunas
    for k,v in metrics.items():    
        dados_estad_mensal[f'{v}_ma'] = dados_estad_mensal.groupby('estadiamento')[v].rolling(window=6).mean().reset_index(0,drop=True)
    
    #remove dois primeiros anos de dados
    dados_estad_mensal = dados_estad_mensal[dados_estad_mensal.data.dt.date >= datetime.date(2010,1,1)]    
    
    dados_estad_mensal.sort_values(by='data', inplace=True)
    return dados_estad_mensal

bucket_name = "observatorio-oncologia"
# file_path = r"monitor/SP/consolidado/dados_estad_mensal.parquet.gzip"

# nome da pasta do projeto
project_folder_name = 'monitor'
dev_lake_name = "lake-rosa-dev"
lake_zone = "silver"
database_name = "cancer_data"

database_location = f'{dev_lake_name}/{lake_zone}'  # Substitua com o local do seu banco de dados Delta Lake
final_parquet_folder = f'{database_location}/{database_name}.db/dados_estados_mensal/'
dados_estad_mensal = read_file(bucket_name, final_parquet_folder)

def space(num_lines=1):
    """Adds empty lines to the Streamlit app."""
    for _ in range(num_lines):
        st.write("")

       
   
# Data visualisation part

st.title(f"Monitor Rosa - dados mensais (câncer de mama)")
# st.dataframe(dados_estad_mensal)
source = dados_estad_mensal
all_symbols = dados_estad_mensal.estadiamento.unique()
symbols = st.multiselect("Estadiamentos", all_symbols, all_symbols)

metrics_selector = st.selectbox(
    "Métrica",
    list(metrics.keys())
)
y_column_name = metrics[metrics_selector]
ma_option = st.checkbox('Média móvel (6 meses)')
if ma_option:
    y_column_name = f'{metrics[metrics_selector]}_ma'

# min_date = dados_estad_mensal.data.dt.date[0]
# max_date = dados_estad_mensal.data.dt.date[-1]
# min_date = datetime.date(2020,1,1)
# max_date = datetime.date(2022,1,1)
# a_date = st.date_input("Período", (min_date, max_date))

space(1)
dataset = dados_estad_mensal[dados_estad_mensal.primeiro_estadiamento.isin(symbols)]
fig = px.line(
    dataset, 
    x='data', 
    y=y_column_name, 
    color='estadiamento', 
    symbol="estadiamento")



# Update layout (yaxis title and responsive legend)
fig.update_layout(
    yaxis_title=metrics_selector,
    legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0.01
            )    
)

st.plotly_chart(
    fig, 
    use_container_width=True)

space(2)

#st.table(dataset)

# inspirações para atualizar o dash
# https://blog.streamlit.io/how-to-build-a-real-time-live-dashboard-with-streamlit/
