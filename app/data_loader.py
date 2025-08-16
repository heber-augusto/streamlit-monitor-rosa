import pandas as pd
import datetime

def read_file(filepath):
    dados = pd.read_csv(filepath)
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
