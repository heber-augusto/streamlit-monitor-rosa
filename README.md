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

---

## Estrutura do Projeto

```
streamlit-monitor-rosa/
│
├── streamlit_app.py         # Arquivo principal da aplicação Streamlit
├── data/                    # Pasta para arquivos de dados (csv, etc)
│
├── app/                     # Módulos Python organizados
│   ├── __init__.py
│   ├── data_loader.py       # Funções de leitura e preparação dos dados
│   ├── utils.py             # Funções utilitárias
│   └── plot.py              # Funções de visualização
│
├── requirements.txt
├── pyproject.toml
├── README.md
```

### Descrição dos principais arquivos
- `streamlit_app.py`: ponto de entrada da aplicação, responsável pela interface e orquestração dos módulos.
- `app/data_loader.py`: funções para leitura e preparação dos dados.
- `app/utils.py`: funções utilitárias, como espaçamento na interface.
- `app/plot.py`: funções para geração de gráficos e visualizações.
- `data/`: pasta sugerida para armazenar arquivos de dados locais (ex: CSV).

---

## Configuração dos Secrets

Para que a aplicação funcione corretamente em uma execução local, é necessário configurar alguns secrets no Streamlit. Crie o arquivo `.streamlit/secrets.toml` na raiz do projeto com o seguinte conteúdo:

```toml
[googledrive]
# Dados do serviço do Google Drive (JSON)
client_email = "..."
private_key = "..."
# ...demais campos do JSON de credenciais...

google_drive_file_id = "<ID do arquivo no Google Drive>"
```

**Atenção:** nunca compartilhe suas credenciais em repositórios públicos.

---
