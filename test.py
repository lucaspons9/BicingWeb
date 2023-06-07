import streamlit as st
import json
import requests
import pandas as pd

def load():
    #acceso al servicio web del bicing
    r = requests.get('https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status')
    bicingJson = r.json()

    dic = {'car': 332,
    'dalmases': 329,
    'upc_abajo': 422,
    'esade': 302,
    'cuartel': 429,
    'pedralbes': 303,
    'upper': 304}

    dic_real = {}
    b_car = bicingJson['data']['stations']
    for key in dic.keys():
        for i in range(len(b_car)):
            if (b_car[i]['station_id'] == dic[key]):
                dic_real[key] = i

    bicis_sitios = {}
    for key in dic_real.keys():
        bicis_sitios[key] = [bicingJson['data']['stations'][dic_real[key]]['num_bikes_available_types']['mechanical'],
                             bicingJson['data']['stations'][dic_real[key]]['num_bikes_available_types']['ebike'],
                             bicingJson['data']['stations'][dic_real[key]]['num_docks_available']]

    df = pd.DataFrame(columns = ['Estación','Mecánicas', 'Eléctricas', 'Sitios Libres'])
    for key in bicis_sitios.keys():
        df.loc[len(df)] = [key, bicis_sitios[key][0], bicis_sitios[key][1], bicis_sitios[key][2]]

    return df


if st.button('Load data'):
    df = load()
    m = df.iloc[0]['Mecánicas']
    e = df.iloc[0]['Eléctricas']
    st.markdown(f'Mecánicas ➡️ {m} \n + Eléctricas ➡️ {e}')
    st.markdown('\n')

    first = -1
    second = -1
    for i in range(6, 1, -1):
        if df.iloc[i]['Sitios Libres'] != 0:
            second = first
            first = i

    if first != -1:
        est_fin_first = df.iloc[first]['Estación']
        sit_first = df.iloc[first]['Sitios Libres']
        st.markdown(f'##### 1. Dejar en *{est_fin_first}* ({sit_first} Sitios libres)')

    if second != -1:
        est_fin_second = df.iloc[second]['Estación']
        sit_second = df.iloc[second]['Sitios Libres']
        st.markdown(f'##### 2. Dejar en *{est_fin_second}* ({sit_second} Sitios libres)')
    st.markdown('___')
    st.dataframe(df, width = 1000)
