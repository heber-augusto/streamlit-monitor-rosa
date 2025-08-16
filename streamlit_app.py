import streamlit as st
from app.data_loader import read_file, preparar_dados
from app.utils import space
from app.plot import plot_line

metrics = {
    'Número de pacientes em tratamento': 'numero_pacientes',
    'Óbitos': 'obitos',
    'Custo': 'custo_estadiamento',
    'Custo por paciente': 'custo_por_paciente',
    'Número de diagnosticos': 'numero_diagnosticos'
}

st.set_page_config(
    layout="wide",
    page_icon="📈",
    page_title="Monitor Rosa"
)

dados_estad_mensal = read_file('dados_estados_mensal.csv')

st.title("Monitor Rosa - dados mensais (câncer de mama)")

all_states = sorted([s for s in dados_estad_mensal['estado'].dropna().unique() if str(s).lower() != 'nan'])
estados_selecionados = st.multiselect("Estados", all_states, all_states)

all_symbols = [s for s in dados_estad_mensal.estadiamento.unique() if st.session_state.get('estadiamento') is None or s is not None]
symbols = st.multiselect("Estadiamentos", all_symbols, all_symbols)

metrics_selector = st.selectbox(
    "Métrica",
    list(metrics.keys())
)
y_column_name = metrics[metrics_selector]
ma_option = st.checkbox('Média móvel (6 meses)')
if ma_option:
    y_column_name = f'{metrics[metrics_selector]}_ma'

space(1)
filtered_data = preparar_dados(dados_estad_mensal, estados_selecionados, symbols, metrics)

fig = plot_line(filtered_data, y_column_name, metrics_selector)
st.plotly_chart(fig, use_container_width=True)

space(4)
#st.table(filtered_data)
