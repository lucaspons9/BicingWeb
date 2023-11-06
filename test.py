from geopy.distance import geodesic
import pydeck as pdk
import streamlit as st
import json
import requests
import pandas as pd
from pydeck.types import String

def load():
    #acceso al servicio web del bicing
    r = requests.get('https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status')
    bicingJson = r.json()

    # station: station id, prioridad de dejar (negativo) o coger (postivo)
    dic = {'Roux': (332,-4),
    'Dalmases': (329,-1),
    'Vergos': (331,-3),
    'Ganduixer-pau alcover': (330,-2),
    'Upc_abajo': (422,4),
    'Esade': (302, 5),  
    'Cuartel': (429, 3),
    'Pedralbes': (303, 2),
    'Upper': (304, 1)}


    dic_real = {key: (next((i for i, station in enumerate(bicingJson['data']['stations']) if station['station_id'] == id[0]), None), id[1]) for key, id in dic.items()}

    df = pd.DataFrame(columns = ['Estación','Mecánicas', 'Eléctricas', 'SitiosLibres', 'Priority'])
    for key in dic_real.keys():
        df.loc[len(df)] = [key,bicingJson['data']['stations'][dic_real[key][0]]['num_bikes_available_types']['mechanical'],
                             bicingJson['data']['stations'][dic_real[key][0]]['num_bikes_available_types']['ebike'],
                             bicingJson['data']['stations'][dic_real[key][0]]['num_docks_available'], dic_real[key][1]]
    return df


df = load()

if st.button('Load data'):
    df = load()

# coger bici
if df.iloc[0]['Eléctricas'] == 0 and df.iloc[0]['Mecánicas'] == 0:
    st.write(f"Home has no bikes.")
# Sort DataFrame by priority
sorted_df = df.sort_values(by='Priority')
# Iterate through the sorted DataFrame
for _, row in sorted_df.iterrows():
    priority = row['Priority']
    if priority > 0:
        break  # Stop when positive priority is reached
    if row['Eléctricas'] > 1:
        st.markdown(f"#### {row['Estación']}\n * Mecánicas: {row['Mecánicas']}\n * Eléctricas: {row['Eléctricas']}")
        break
    elif row['Eléctricas'] == 1:
        st.markdown(f"#### {row['Estación']}\n * Mecánicas: {row['Mecánicas']}\n * Eléctricas: {row['Eléctricas']}")
        # Find the next station with more than 0 mecánicas or eléctricas
        next_station = sorted_df[
            (sorted_df['Priority'] > priority) &
            ((sorted_df['Mecánicas'] > 0) | (sorted_df['Eléctricas'] > 0))
        ].iloc[0]  # Get the first station that meets the conditions
        st.write(f"Siguiente estación: {next_station['Estación']} tiene {next_station['Mecánicas']} Mecánicas y {next_station['Eléctricas']} eléctricas.")
        break


# Estaciones donde dejar bici
pos_sorted_df = df[(df['Priority'] > 0) & (df['SitiosLibres'] > 0)].sort_values(by='Priority', ascending = False)
s = 2 if len(pos_sorted_df) > 2 else len(pos_sorted_df)
for i in range(s):
    st.markdown(f'##### {i + 1}. Dejar en *{pos_sorted_df.iloc[i]["Estación"]}* ({pos_sorted_df.iloc[i]["SitiosLibres"]} Sitioslibres)')

st.markdown('___')

############

dic = {'Roux': (332,-4),
    'Dalmases': (329,-1),
    'Vergos': (331,-3),
    'Ganduixer-pau alcover': (330,-2),
    'Upc_abajo': (422,4),
    'Esade': (302, 5),  
    'Cuartel': (429, 3),
    'Pedralbes': (303, 2),
    'Upper': (304, 1)}
station_info = requests.get('https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information').json()
dic_real2 = {key: (next((i for i, station in enumerate(station_info['data']['stations']) if station['station_id'] == id[0]), None), id[1]) for key, id in dic.items()}


df_stations = pd.DataFrame(columns = ['Estación', 'lat', 'lon', 'capacity'])
for key in dic_real2:
    stat_info = station_info['data']['stations'][dic_real2[key][0]]
    df_stations.loc[len(df_stations)] = [
        key,
        stat_info['lat'],
        stat_info['lon'],
        stat_info['capacity']
    ]

result = pd.merge(df, df_stations, on='Estación', how='outer')



# Define a function to calculate new coordinates
def calculate_new_coordinates(lon, lat, distance, bearing):
    # Calculate the destination point using geodesic
    destination = geodesic(kilometers=distance / 1000).destination((lat, lon), bearing)
    return destination[1], destination[0]

# Calculate lon2 and lat2, 40 meters west
result['lon2'], result['lat2'] = zip(*result.apply(lambda row: calculate_new_coordinates(row['lon'], row['lat'], 60, 270), axis=1))

# Calculate lon3 and lat3, 40 meters south
result['lon3'], result['lat3'] = zip(*result.apply(lambda row: calculate_new_coordinates(row['lon'], row['lat'], 60, 180), axis=1))




# Create a PyDeck map
st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=41.395885,
        longitude=2.122117,
        zoom=13.5,
        pitch=40,
        bearing=-15
    ),
    layers=[
        pdk.Layer(
            "ColumnLayer",
            data=result,
            get_position=["lon2", "lat2"],
            get_elevation="Mecánicas",
            elevation_scale=10,
            # elevation_range=[0, max_range],
            radius=50,
            get_fill_color=['Mecánicas > 0 ? 200 : 100','Mecánicas > 0 ? 30 : 15','Mecánicas > 0 ? 0 : 0',160],
            pickable=True,
            auto_highlight=True,
        ),
        pdk.Layer(
            "ColumnLayer",
            data=result,
            get_position=["lon3", "lat3"],
            get_elevation="Eléctricas",
            elevation_scale=10,
            # elevation_range=[0, max_range],
            radius=50,
            get_fill_color=['Eléctricas > 0 ? 0 : 10','Eléctricas > 0 ? 102 : 10','Eléctricas > 0 ? 255 : 45',160],
            pickable=True,
            auto_highlight=True,
        ),
        pdk.Layer(
            "ColumnLayer",
            data=result,
            get_position=["lon", "lat"],
            get_elevation="SitiosLibres",
            elevation_scale=10,
            radius=50,
            get_fill_color=[225, 225, 225, 20],
            pickable=True,
            auto_highlight=True,
        ),
        
    ],
))


###########
st.markdown('___')
st.dataframe(df, width = 1000)




