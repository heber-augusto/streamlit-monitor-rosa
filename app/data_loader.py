import pandas as pd
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st

def autenticar_servico(escopos):
    credenciais = service_account.Credentials.from_service_account_info(
        st.secrets["googledrive"], scopes=escopos
    )
    return build('drive', 'v3', credentials=credenciais)

def read_file_from_drive(service, file_id, output_file_name):
    try:
        request = service.files().get_media(fileId=file_id)
        content = request.execute()
        with open(output_file_name, 'wb') as f:
            f.write(content)
        print(f"File '{output_file_name}' downloaded successfully.")
    except HttpError as error:
        print(f'An API error occurred: {error}')

@st.cache_data(ttl=3600)
def read_file(google_drive_file_id):
    escopos = ['https://www.googleapis.com/auth/drive.readonly']
    service = autenticar_servico(escopos)
    read_file_from_drive(
        service,
        google_drive_file_id,
        output_file_name='dados_estados_mensal.csv')
    dados = pd.read_csv('dados_estados_mensal.csv')
    dados['data'] = pd.to_datetime(dados['data'], format='%Y%m')
    dados['estadiamento'] = dados['primeiro_estadiamento']
    return dados

def preparar_dados(dados, estados_selecionados, estadiamentos_selecionados, metrics):
    dados = dados[
        dados['estadiamento'].notna() & (dados['estadiamento'] != '')
    ]
    if estados_selecionados:
        dados = dados[dados['estado'].isin(estados_selecionados)]
    if estadiamentos_selecionados:
        dados = dados[dados['estadiamento'].isin(estadiamentos_selecionados)]
    dados['custo_por_paciente'] = (
        dados['custo_estadiamento'] / dados['numero_pacientes']
    )
    for k, v in metrics.items():
        dados[f'{v}_ma'] = (
            dados.groupby(['estadiamento', 'estado'])[v]
            .transform(lambda x: x.rolling(window=6).mean())
        )
    dados = dados[dados.data.dt.date >= datetime.date(2010, 1, 1)]
    dados.sort_values(by='data', inplace=True)
    if estados_selecionados and len(estados_selecionados) > 1:
        group_cols = ['data', 'estadiamento']
        agg_dict = {v: 'sum' for v in metrics.values()}
        agg_dict['custo_por_paciente'] = 'sum'
        for k, v in metrics.items():
            agg_dict[f'{v}_ma'] = 'sum'
        dados = dados.groupby(group_cols).agg(agg_dict).reset_index()
    return dados
