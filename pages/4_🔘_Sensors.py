import time

import streamlit as st
from api import APIManager, fetch_data, make_request

st.set_page_config(page_title="Sensors",
                   page_icon="🔌",
                   layout="wide",
                   initial_sidebar_state='expanded')

from sensor_card import sensor_card

st.header('Edit a sensor', divider='rainbow')
st.markdown('Assign a new name to a sensor.')

rooms, room_status  = fetch_data(APIManager.ROOMS_ENDPOINT)
sensors, sensor_status = fetch_data(APIManager.SENSORS_ENDPOINT)

if room_status >= 400 or sensor_status >= 400:
    st.error(sensors)
    st.button('Retry', type='primary')
else:
    room_names = [room['name'] for room in rooms]
    sensors_select_options = [sensor['name'] for sensor in sensors]

    selected_sensor_name = st.selectbox(
            '#### Select',
            options=sensors_select_options,
            index=0)
    

    selected_sensor = next(sensor for sensor in sensors if selected_sensor_name == sensor['name'])
    selected_sensor['device']['room'] = next((room['name'] for room in rooms if room['id'] == selected_sensor['device']['room']), None)

    sensor_card(selected_sensor)

    with st.form("edit_sensor_form", border=False):

        sensor_name = st.text_input("Assign a name")

        submitted = st.form_submit_button("Submit changes", type='primary')

        if submitted and sensor_name:
            response_data, response_status = make_request(
                        url=APIManager.SENSORS_ENDPOINT,
                        id=selected_sensor['id'],
                        data={'name': sensor_name},
                        method='PATCH')
            
            if response_status >= 400:
                st.error(
                    f"Failed to rename sensor. Reason was \n**{', '.join(str(value) for value in response_data.values())}**")
            else:
                st.success(
                    f"Sensor with serial **\"{response_data['serial']}\"** was successfully renamed to **\"{response_data['name']}\"**.")
                time.sleep(3)
                st.rerun()