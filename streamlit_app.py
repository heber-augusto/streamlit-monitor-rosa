from datetime import datetime
from io import BytesIO

import streamlit as st
from vega_datasets import data

from utils import chart, db
from google.oauth2 import service_account
from google.cloud import storage
import pandas as pd

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)


# Retrieve file contents.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def read_file(bucket_name, file_path):
    bucket = client.bucket(bucket_name)
    content = bucket.blob(file_path).download_as_string().decode("utf-8")
    return content

bucket_name = "observatorio-oncologia"
file_path = r"monitor/SP/consolidado/dados_estad_mensal.parquet.gzip"

content = read_file(bucket_name, file_path)

bytes_io = BytesIO(content.readall())
df = pd.read_parquet(bytes_io)


def space(num_lines=1):
    """Adds empty lines to the Streamlit app."""
    for _ in range(num_lines):
        st.write("")


st.set_page_config(layout="centered", page_icon="💬", page_title="Commenting app")

# Data visualisation part

st.title(f"💬 Commenting app {len(df.index)}")

source = data.stocks()
all_symbols = source.symbol.unique()
symbols = st.multiselect("Choose stocks to visualize", all_symbols, all_symbols[:3])

space(1)

source = source[source.symbol.isin(symbols)]
chart = chart.get_chart(source)
st.altair_chart(chart, use_container_width=True)

space(2)

