from datetime import datetime
from io import BytesIO

import streamlit as st

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import datetime

import plotly.express as px


st.set_page_config(
    layout="wide", 
    page_icon="📈", 
    page_title="Monitor Rosa")


# Create API client.
#credentials = service_account.Credentials.from_service_account_info(
#    st.secrets["gcp_service_account"]
#)
#client = storage.Client(credentials=credentials)


metrics = {
 'Número de pacientes em tratamento': 'numero_pacientes',   
 'Óbitos':'obitos',
 'Custo':'custo_estadiamento',
 'Custo por paciente': 'custo_por_paciente',
 'Número de diagnosticos': 'numero_diagnosticos'      
}




def autenticar_servico(json_caminho, escopos):
    credenciais = service_account.Credentials.from_service_account_file(json_caminho, scopes=escopos)
    return build('drive', 'v3', credentials=credenciais)


def read_file_from_drive(service, file_id, output_file_name):
    """Reads the content of a file from Google Drive by its ID and saves it to a local file."""
    try:
        # Call the Drive v3 API
        # You can specify the mimeType if you know it, or handle different types
        # This example focuses on text/plain or similar readable files
        request = service.files().get_media(fileId=file_id)

        # Download the file content
        # For larger files, you might need to use MediaIoBaseDownload
        content = request.execute()

        # Save the content to the specified output file
        with open(output_file_name, 'wb') as f:
            f.write(content)
        print(f"File '{output_file_name}' downloaded successfully.")

    except HttpError as error:
        print(f'An API error occurred: {error}')




# Retrieve file contents.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=3600)
def read_file(google_drive_file_id):

    auth_json_path='monitor-rosa-leitura.json'
    escopos = ['https://www.googleapis.com/auth/drive.readonly']
    service = autenticar_servico(auth_json_path, escopos)

    read_file_from_drive(
        service,
        google_drive_file_id,
        output_file_name='dados_estados_mensal.csv')    

    dados_estad_mensal = pd.read_csv('dados_estados_mensal.csv')

    dados_estad_mensal['data'] = pd.to_datetime(
        dados_estad_mensal['data'], format='%Y%m')
    # renomeia coluna
    dados_estad_mensal['estadiamento'] = dados_estad_mensal['primeiro_estadiamento']

    # Remove dados de estadiamento vazio, nulo ou NaN e filtra estado
    dados_estad_mensal = dados_estad_mensal[
        (dados_estad_mensal['estadiamento'].notna()) &
        (dados_estad_mensal['estadiamento'] != '') &
        (dados_estad_mensal['estado'] == 'São Paulo')
    ]
    dados_estad_mensal['custo_por_paciente'] = (
        dados_estad_mensal['custo_estadiamento'] / dados_estad_mensal['numero_pacientes']
    )

    # Cria média móvel para cada coluna
    for k, v in metrics.items():
        dados_estad_mensal[f'{v}_ma'] = (
            dados_estad_mensal.groupby('estadiamento')[v]
            .rolling(window=6).mean().reset_index(0, drop=True)
        )

    # Remove dois primeiros anos de dados
    dados_estad_mensal = dados_estad_mensal[
        dados_estad_mensal.data.dt.date >= datetime.date(2010, 1, 1)
    ]
    dados_estad_mensal.sort_values(by='data', inplace=True)
    return dados_estad_mensal

dados_estad_mensal = read_file(
    google_drive_file_id='140mI8ZZGBDqPUtJXkoSFFGWzCcRPduJv'
)

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
