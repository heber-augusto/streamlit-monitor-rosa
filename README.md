[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monitor-rosa.streamlit.app/)

# Monitor Rosa

Aplicação para mostrar série histórica de métricas (custo, óbitos e número de pacientes) registrados em procedimentos de quimioterapia e radioterapia, de pacientes com câncer de mama.

---

## Instalação do Ambiente com Poetry

Este projeto utiliza o [Poetry](https://python-poetry.org/) para gerenciamento de dependências e ambiente virtual.

### Pré-requisitos
- Python 3.12 ou superior

### Passos para Instalação

1. **Instale o Poetry** (caso não tenha):
	```bash
	curl -sSL https://install.python-poetry.org | python3 -
	```
	Ou siga as instruções oficiais: https://python-poetry.org/docs/#installation

2. **Clone o repositório:**
	```bash
	git clone https://github.com/heber-augusto/streamlit-monitor-rosa.git
	cd streamlit-monitor-rosa
	```

3. **Instale as dependências:**
	```bash
	poetry install
	```

4. **Ative o ambiente virtual do Poetry:**
    ```bash
    source $(poetry env info --path)/bin/activate
    ```
    Consulte a documentação oficial para detalhes: https://python-poetry.org/docs/managing-environments/#activating-the-environment

5. **Execute o Streamlit:**
	```bash
	streamlit run streamlit_app.py
	```

Pronto! A aplicação estará disponível localmente.
