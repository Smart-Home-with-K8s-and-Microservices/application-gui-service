from datetime import datetime
import time

import pandas as pd
import streamlit as st
from api import APIManager, fetch_data, make_request, post_data

st.set_page_config(page_title="Actions",
                   page_icon="🏭",
                   layout="wide",
                   initial_sidebar_state='expanded')

st.header('🏭 Actions', divider='rainbow')
st.markdown(
    'Action is an event.')

def get_comparison_type(operator):
    if operator == '>':
        return 'greater than'
    elif operator == '<':
        return 'less than'
    elif operator == '=':
        return 'equal to'


st.markdown('### All actions')

actions, action_status = fetch_data(APIManager.ACTIONS_ENDPOINT)
sensors, sensor_status = fetch_data(APIManager.SENSORS_ENDPOINT)

if action_status >= 400:
    st.error(actions)
    st.button('Retry', type='primary')
else:
    # cont = st.container(border=False, height = 200)
    # pop = st.popover(label='Actions')

    if actions:
        for action in actions:
            action['initiator_sensor'] = next(sensor['name'] for sensor in sensors if action['initiator_sensor'] == sensor['id'])
            action['recipient_sensor'] = next(sensor['name'] for sensor in sensors if action['recipient_sensor'] == sensor['id'])
            
            # cont = st.expander(label=f'{"🟢" if action["active"] else "🔴"} **Action #{action["id"]}**')
            cont = st.container(border=True)
            
            cont.markdown(f'#### {"🟢" if action["active"] else "🔴"} Action #{action["id"]}')
            cont.markdown(f'Send command :grey["{action["command"]}"] to :grey["{action["recipient_sensor"]}"] if value of :grey["{action["initiator_sensor"]}"] is {get_comparison_type(action["comparison_type"])} :grey[{action["check_value"]}].')
            

            created_dt = datetime.fromisoformat(action["created_at"].replace("Z", "+00:00"))
            updated_dt = datetime.fromisoformat(action["updated_at"].replace("Z", "+00:00"))
            
            converted_created_at = created_dt.strftime("%B %d, %Y, %I:%M:%S %p %Z")
            converted_updated_dt = updated_dt.strftime("%B %d, %Y, %I:%M:%S %p %Z")
            cont.caption(f'Created at: {converted_created_at} | Updated at: {converted_updated_dt}')

            cont1, cont2 = cont.columns(2)

            activated = cont1.button('Activate', key=action['id'] * 1.7, use_container_width=True, disabled=action['active'])
            if activated:
                data, status = make_request(url=APIManager.ACTIONS_ENDPOINT, id=action['id'], method='PATCH', data={'active': True})
                if status >= 400:
                    st.toast(icon='🚨', body=f"Error activating the selected action. {data}")
                else:
                    st.toast(icon='✅️', body='Action was activated successfully.')
                    time.sleep(2)
                    st.rerun()
                    
            delete = cont2.button('Delete', key=action['id'] * 1.2, use_container_width=True)
            if delete:
                data, status = make_request(url=APIManager.ACTIONS_ENDPOINT, id=action['id'], method='DELETE')
                if status >= 400:
                    st.toast(icon='🚨', body=f"Error deleting the selected action. {data}")
                else:
                    st.toast(icon='✅️', body='Action was deleted successfully.')
                    time.sleep(2)
                    st.rerun()

    else:
        st.markdown('No actions found.')
    
    initiators_select_options = [sensor['name'] for sensor in sensors]
    recipients_select_options = [sensor['name'] for sensor in sensors if sensor['accepts_commands']]


    st.markdown('### Set an action')
    with st.form("edit_sensor_form", border=True):
        col1, col2, col3 = st.columns(3)
        selected_initiator_name = col1.selectbox(
                'Select sensor to check its value',
                options=initiators_select_options,
                index=0)

        initiator_sensor = next(sensor for sensor in sensors if selected_initiator_name == sensor['name'])
        
        selected_operator = col2.selectbox(
                'Select comparison operator',
                options=['<', '>', '='],
                index=0)

        value_to_check = col3.number_input("Enter value to check")
        
        col1, col2 = st.columns(2)
        
        selected_recipient_name = col1.selectbox(
                'Select sensor to trigger',
                options=recipients_select_options,
                index=0)

        recipient_sensor = next(sensor for sensor in sensors if selected_recipient_name == sensor['name'])
        
        selected_command = col2.selectbox(
                'Select command',
                options=recipient_sensor['available_commands'],
                index=0)

        submitted = st.form_submit_button("Submit", type='primary')

        action_data = {
            "initiator_sensor": initiator_sensor['id'],
            "recipient_sensor": recipient_sensor['id'],
            "check_value": value_to_check,
            "comparison_type": selected_operator,
            "command": selected_command,
            "active": True
        }


        if submitted:
            response_data, response_status = post_data(APIManager.ACTIONS_ENDPOINT, action_data)
            if response_status >= 400:
                st.error(
                    f"Failed to set action. Reason was \n**{response_data}**")
            else:
                st.success(f"Action was successfully set.")
                time.sleep(3)
                st.rerun()