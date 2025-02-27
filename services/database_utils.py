import streamlit as st
import pandas as pd

from google.oauth2 import service_account
from google.cloud import bigquery




def load_panoply(query):

    credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    query_job = client.query(query)
    rows_raw = query_job.result()
    rows = [dict(row) for row in rows_raw]
    return pd.DataFrame(rows)


@st.cache_data(ttl='4h', show_spinner='Fetching new data...')
def get_fis_points():

    query_points = f"""
    SELECT * FROM `panoply.fis_points_aktuell`
    WHERE listid = (SELECT MAX(listid) FROM `panoply.fis_points_aktuell`)
    """

    df = load_panoply(query_points)

    df["birthyear"] = df["birthyear"].astype(str)

    return df