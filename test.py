import streamlit as st
import json
import requests
import pandas as pd

def load():
    #acceso al servicio web del bicing
    r = requests.get('http://wservice.viabicing.cat/v2/stations')
    bicingJson = r.json()

    dic = {'Casa': 332,
    'Dalmases': 329,
    #'upc_abajo': 422,
    #'upc_arriba': 429
    'Esade': 302,
    'Pedralbes': 303,
    'Upper': 304}

    dic_real = {}

    b_casa = bicingJson['stations']
    for key in dic.keys():
        for i in range(len(b_casa)):
            if (b_casa[i]['id'] == str(dic[key])):
                dic_real[key] = i

    bicis_sitios = {}
    for key in dic_real.keys():
        bicis, sitios = bicingJson['stations'][dic_real[key]]['bikes'],bicingJson['stations'][dic_real[key]]['slots']
        bicis_sitios[key] = [bicis, sitios]

    df = pd.DataFrame(columns = ['Estación','Bicis', 'Sitios'])
    for key in bicis_sitios.keys():
        # df.append({'Estación': key, 'Bicis': bicis_sitios[key][0], 'Sitios': bicis_sitios[key][1]}, ignore_index=True)
        df.loc[len(df)] = [key, bicis_sitios[key][0], bicis_sitios[key][1]]

    return df


if st.button('Load data'):
    df = load()
    if df.iloc[0]['Bicis'] != '0':
        est_ini = 'Casa'
    elif df.iloc[1]['Bicis'] != '0':
        est_ini = 'Dalmases'
    else:
        est_ini = None
    st.markdown(f'### Coger en *{est_ini}*')
    if df.iloc[2]['Sitios'] != '0':
        est_fin = df.iloc[2]['Estación']
    elif df.iloc[3]['Sitios'] != '0':
        est_fin = df.iloc[3]['Estación']
    elif df.iloc[4]['Sitios'] != '0':
        est_fin = df.iloc[4]['Estación']
    else:
        est_fin = None
    st.markdown(f'### Dejar en *{est_fin}*')
    st.dataframe(df, width = 1000)
