import altair as alt
import pandas as pd
import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="IoT Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

from influxdb import get_device_status
from api import (
    APIManager, fetch_data)
from sensor_card import sensor_card

st.title("Dashboard")

sensor_data, sensor_status = fetch_data(APIManager.SENSORS_ENDPOINT)
device_data, device_status = fetch_data(APIManager.DEVICE_ENDPOINT)
room_data, room_status = fetch_data(APIManager.ROOMS_ENDPOINT)

if room_status >= 400 or sensor_status >= 400 or device_status >= 400:
    st.error(sensor_data)
    st.button('Retry', type='primary')
else: 

    room_radio_options = [room['name'] for room in room_data]


    room_radio_options.insert(0, 'All')

    st.subheader('Rooms', divider='rainbow')
    selected_room = st.radio('Select room', room_radio_options, horizontal=True, label_visibility='collapsed')


    st.subheader('Active sensors', divider='rainbow')

    alt.themes.enable("dark")
    alt.themes.enable()


    for device in device_data:
        status = get_device_status(device_serial=device['serial'])
        device['room'] = next((room['name'] for room in room_data if room['id'] == device['room']), None)
        if status:
            st.toast(f'Device "{device["name"]}" went {status}!')
            time.sleep(2)
            

    num_sensors = len(sensor_data)
    active_sensors = 0
    cols = st.columns(2)  # Create 3 columns for sensor info
    # Loop through the sensors and display them in rows of 2
    for i, sensor in enumerate(sensor_data):
        sensor['device']['room'] = next((room['name'] for room in room_data if room['id'] == sensor['device']['room']), None)
        
        if selected_room != 'All' and sensor['device']['room'] != selected_room:
            continue
        
        if sensor['device']['status'] != 'connected':
            continue
        # # Calculate the column and row index
        col_index = i % 2
        row_index = i // 2

        # Access the corresponding column based on the column index
        with cols[col_index]:
            sensor_card(sensor)

        active_sensors += 1

    if not active_sensors:
        st.markdown('No active sensors found.')

    st.subheader('Devices', divider='rainbow')


    if not device_data:
        st.markdown('No devices found.')
    else:
        
        filtered_devices = [device for device in device_data if selected_room == 'All' or device['room'] == selected_room]
        # Create a DataFrame
        df = pd.DataFrame({
            'Name': [device['name'] for device in filtered_devices],
            'Model': [device['model'] for device in filtered_devices],
            'Serial': [device['serial'] for device in filtered_devices],
            'Room': [device['room'] for device in filtered_devices],
            'Status': [device['status'] for device in filtered_devices],
        })

        # Display the DataFrame
        st.table(df)

    refresh_count = st_autorefresh(interval=2000, limit=None, key='fizzmonkey')
