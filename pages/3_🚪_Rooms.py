import streamlit as st
import pandas as pd
import time
from api import fetch_data, APIManager, make_request

st.set_page_config(page_title="Rooms",
                   page_icon="🚪",
                   layout="wide",
                   initial_sidebar_state='expanded')

st.header('🚪Rooms', divider='rainbow')
st.markdown(
    'Create a new entry for a room by adding a name and optionally a description for it.')

rooms, status = fetch_data(APIManager.ROOMS_ENDPOINT)

if status >= 400:
    st.error(rooms)
    st.button('Retry', type='primary')
else: 
    rooms_dataframe = pd.DataFrame({
        'Name': [room['name'] for room in rooms],
        'Description': [room['description'] for room in rooms],
    })

    room_table = st.dataframe(
        rooms_dataframe, use_container_width=True, hide_index=True)

    NEW_ROOM_OPTION = '-- Add a new room --'
    room_names = [room['name'] for room in rooms]
    room_names.insert(0, NEW_ROOM_OPTION)

    with st.container(border=True):
        selected_room_name = st.selectbox(
            '#### Select',
            options=room_names,
            index=0)
        selected_room = next((room for room in rooms if selected_room_name == room['name']), None)

        room_cont = st.container(border=True)
        if selected_room_name != NEW_ROOM_OPTION:
            room_cont.markdown(f"### 🚪 {selected_room['name']}")
            room_cont.markdown(f"{selected_room['description']}")
            delete_pressed = room_cont.button('Delete', disabled=(selected_room_name==NEW_ROOM_OPTION))
            if delete_pressed:
                _, status = make_request(url=APIManager.ROOMS_ENDPOINT, id=selected_room['id'], method='DELETE')
                if status >= 400:
                    st.toast(f'Failed to delete room {selected_room["name"]}')
                else:
                    st.toast(f'Room {selected_room["name"]} was deleted successfully!')
                    time.sleep(3)
                    st.rerun()
        with st.form("edit_device_form", border=False):
            if selected_room_name == NEW_ROOM_OPTION:
                st.markdown("#### Create a room")  
            else:
                st.markdown("#### Edit")

            room_data = {}

            room_name = st.text_input("Room name")
            room_description = st.text_area('Add a description')

            if room_name:
                room_data.update({'name': room_name})
            if room_description:
                room_data.update({'description': room_description})

            submitted = st.form_submit_button("Confirm", type='primary')

            if submitted and room_data:
                if not selected_room:
                    response_data, response_status = make_request(
                        url=APIManager.ROOMS_ENDPOINT,
                        data=room_data,
                        method='POST')
                else:
                    response_data, response_status = make_request(
                        url=APIManager.ROOMS_ENDPOINT,
                        id=selected_room['id'],
                        data=room_data,
                        method='PATCH')
                if response_status >= 400:
                    st.error(
                        f"Failed to create room. Reason was \n**{', '.join(str(value) for value in response_data.values())}**")
                else:
                    st.success(
                        f"Room with name **\"{response_data['name']}\"** was created or updated.")
                    time.sleep(3)
                    st.rerun()