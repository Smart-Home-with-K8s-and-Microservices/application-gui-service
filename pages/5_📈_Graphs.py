import streamlit as st
from api import APIManager, fetch_data
from sensor_card import sensor_card

st.set_page_config(
    page_title="Analytics",
    layout="wide",
    initial_sidebar_state="expanded")

from influxdb import connect_to_influxdb, get_device_data, get_sensor_data

st.header('Graphs', divider='rainbow')
st.markdown(
    'Here are displayed useful graphs regarding sensor data.')

rooms, room_status  = fetch_data(APIManager.ROOMS_ENDPOINT)
sensors, sensor_status = fetch_data(APIManager.SENSORS_ENDPOINT)

if room_status >= 400 or sensor_status >= 400:
    st.error(sensors)
    st.button('Retry', type='primary')

room_names = [room['name'] for room in rooms]
sensors_select_options = [f"{sensor['serial']}" for sensor in sensors]

selected_sensor_serial = st.selectbox(
        '#### Select sensor',
        options=sensors_select_options,
        index=0)

selected_sensor = next(sensor for sensor in sensors if selected_sensor_serial == sensor['serial'])
selected_sensor['device']['room'] = next((room['name'] for room in rooms if room['id'] == selected_sensor['device']['room']), None)

sensor_card(selected_sensor)

influxdb_client = connect_to_influxdb()

last_week_chart = get_sensor_data(influxdb_client, selected_sensor_serial, '-7d', '1m', None)

last_week_chart.rename(columns={"_time": "Time","data": "Data"},
                inplace=True)

last_24hours_chart = get_sensor_data(influxdb_client, selected_sensor_serial, '-1d', '1m', None)
last_24hours_chart.rename(columns={"_time": "Time", "data": "Data"},
                inplace=True)

last_hour_chart = get_sensor_data(influxdb_client, selected_sensor_serial, '-1h', '1m', None)
last_hour_chart.rename(columns={"_time": "Time", "data": "Data"},
                inplace=True)


col1, col2 = st.columns(2)

col1.subheader('Last hour', divider='rainbow')
if not last_hour_chart.empty:
    col1.line_chart(last_hour_chart, x='Time', y='Data')
else:
    col1.markdown('No data found for this period of time.')

col2.subheader("Last 24 hours", divider='rainbow')
if not last_24hours_chart.empty:
    col2.line_chart(last_24hours_chart, x='Time', y='Data')
else:
    col2.markdown('No data found for this period of time.')

st.subheader("Last week", divider='rainbow')
if not last_week_chart.empty:
    st.line_chart(last_week_chart, x='Time', y='Data')
else:
    st.markdown('No data found for this period of time.')

col1, col2 = st.columns(2)

col1.subheader('Device status (last 24 hours)', divider='rainbow')

device_status_last_7days = get_device_data(influxdb_client, selected_sensor['device']['serial'], '-7d')
device_status_last_24hours = get_device_data(influxdb_client, selected_sensor['device']['serial'], '-24h')

if not device_status_last_24hours.empty:
    col1.line_chart(device_status_last_24hours, x='_time', y='status', height=280)
else:
    col1.markdown('No data found for this period of time.')

col2.subheader('Device logs (last 7 days)', divider='rainbow')
if not device_status_last_7days.empty:
    col2.dataframe(device_status_last_7days, use_container_width=True)
else:
    col2.markdown('No data found for this period of time.')
        
