import streamlit as st
import pandas as pd
import time
from api import APIManager, fetch_data, make_request, flash_device, get_connected_device

st.set_page_config(page_title="Devices",
                   page_icon="🔌",
                   initial_sidebar_state='expanded')

st.header('Edit a device', divider='rainbow')
st.markdown('Give a desired name to your device')

# Fetch data from the API
devices, device_status = fetch_data(APIManager.DEVICE_ENDPOINT)
rooms, room_status  = fetch_data(APIManager.ROOMS_ENDPOINT)

if room_status >= 400 or device_status >= 400:
    st.error(rooms)
    st.button('Retry', type='primary')
else:
        
    room_names = [room['name'] for room in rooms]

    if devices:
        device_serials = [device["serial"] for device in devices]

        selected_serial = st.selectbox(
            '#### Select a device', options=device_serials)

        if selected_serial:
            selected_device = next(
                device for device in devices if device['serial'] == selected_serial)

            selected_room_serial = selected_device.get('room')

            room_name = next(
                (room['name'] for room in rooms if room['id'] == selected_room_serial), None)

            df = pd.DataFrame({
                'Name': [selected_device['name']],
                'Serial': [selected_device['serial']],
                'Model': [selected_device['model']],
                'Room': [room_name],
                'Status': [selected_device['status']],
            })

            cont = st.container(border=True)
            cont.markdown(f"#### 🔌 Device \"{selected_device['name']}\"")
            cont.table(df)
            cont.caption('Device information')

            with st.form("edit_device_form", border=False):
                st.markdown(f"#### Edit device")

                updated_data = {}

                new_device_name = st.text_input("Assign a new name", placeholder='e.g. device on shelf')
                selected_room_name = st.selectbox(
                    'Assign a room for the device', options=room_names, index=None)

                if new_device_name:
                    updated_data.update({'name': new_device_name})
                if selected_room_name:
                    room_id = next(
                        room['id'] for room in rooms if room['name'] == selected_room_name)
                    updated_data.update({'room': room_id})
                submitted = st.form_submit_button("Submit changes", type='primary')

                if submitted and updated_data:
                    response = make_request(
                        url=APIManager.DEVICE_ENDPOINT,
                        id=selected_device['id'],
                        data=updated_data,
                        method='PATCH')
                    if response:
                        if new_device_name:
                            st.toast(
                                f"Device with serial **\"{selected_device['serial']}\"** renamed to **\"{new_device_name}\"**")
                        if selected_room_name:
                            st.toast(
                                f"Device with serial **\"{selected_device['serial']}\"** was assigned to **\"{selected_room_name}\"**")
                    else:
                        st.toast(
                            f"Failed to update device with serial **\"{selected_device['serial']}\"**", icon='❌')
                    time.sleep(3)
                    st.rerun()

st.header('Configure a connected device', divider='rainbow')
st.markdown('Connect a device to the Rasppberry Pi server and configure a device by providing your WiFi credentials.')


def cancel_configuration():
    st.session_state.configure = None


if 'credentials' not in st.session_state:
    st.session_state.credentials = None

if 'configure' not in st.session_state:
    st.session_state.configure = None

if st.button("Search for device", type='primary'):
    st.session_state.configure = True

if st.session_state.configure:
    with st.status("Searching for connected device...", expanded=True) as status:
        st.write('')
        found_device = get_connected_device()
        if found_device and found_device.get('error') is None:
            st.markdown('#### Device information')
            status.update(label="Device found!", state="complete")

            df = pd.DataFrame({
                'Name': [found_device["name"]],
                'Model': [found_device["model"]],
                'Serial': [found_device["serial"]],
                'Status': [found_device["status"]]

            })
            st.table(df)
            st.markdown("#### Configure device")
            with st.form("my_form"):
                wifi_ssid = st.text_input("WiFi SSID")
                wifi_password = st.text_input("WiFi Password", type="password")
                server_ip = st.text_input('Raspberry Pi IP Address')
                # Every form must have a submit button.
                submitted = st.form_submit_button(
                    "Flash device", type='primary')
                if submitted:
                    st.session_state.configure = False
                    st.session_state.credentials = [
                        found_device['id'], wifi_ssid, wifi_password, server_ip]
                    st.rerun()
        else:
            status.update(label="Error while searching!", state="error")
            if found_device:
                st.error(
                    body=found_device.get('error'))

        st.button('Cancel', on_click=cancel_configuration,
                  type='secondary', use_container_width=True)

if st.session_state.credentials:
    with st.status("Attempt to flash connected device...", expanded=True) as status:
        time.sleep(2)
        text, status = flash_device(*st.session_state.credentials)
        if status != 200:
            st.markdown('#### There was an error while flashing.')
            st.error(text)
        else:
            st.markdown('#### Success!')
            st.success(text)
        st.session_state.credentials = None