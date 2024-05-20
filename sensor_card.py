import streamlit as st
from api import send_command
from datetime import datetime
from influxdb import get_last_value

def get_emoji(sensor_type):
    if sensor_type == 'Light Intensity':
        return '☀️'
    elif sensor_type == 'Relay':
        return '🎚️'
    elif sensor_type == 'Temperature':
        return '🌡️'
    elif sensor_type == 'Humidity':
        return '💧'
    elif sensor_type == 'Motion Detection':
        return '🏃‍♀️'

def get_transformed_value(sensor_type, value):
    if sensor_type == 'Light Intensity':
            return f'{round(100 * (value / 200), 1)} %'
    elif sensor_type == 'Relay':
        if value == 1:
            return 'ON'
        elif value == 0:
            return 'OFF'
    elif sensor_type == 'Motion Detection':
        if value == 1:
            return 'Detection!'
        elif value == 0:
            return 'No Detection!'
    elif sensor_type == 'Temperature':
        return f'{value} °C'
    elif sensor_type == 'Humidity':
        return f'{value} %'
    else:
        return value

def get_command_index(value):
    if value == 1:
        return 0
    elif value == 0:
        return 1

def command_manager(container, sensor, value):
    if sensor['available_commands']:
        option = container.radio(
            index=get_command_index(value),
            label="##### Commands",
            options=sensor['available_commands'],
            key=sensor['id'],
            horizontal=True
        )
    
        if sensor['serial'] not in st.session_state:
            st.session_state[sensor['serial']] = option
        elif option != st.session_state[sensor['serial']]:
            st.session_state[sensor['serial']] = option
            response_text = send_command(sensor, option)
            st.toast(f'{response_text}')

    
def sensor_card(sensor):
    cont = st.container(border=True)

    value, measurement_time = get_last_value(sensor['serial'])

    
    cont.markdown(f"### {get_emoji(sensor['type'])} \"{sensor['name']}\" | {sensor['type']}")
    cont.caption(f"On device :green[{sensor['device']['name']}]. Located at :violet[{sensor['device']['room']}].")
    
    if value is not None:
        cont_col1, cont_col2 = cont.columns(2)
        if isinstance(value, float):
            value = round(value, 2)
        cont_col1.metric(label=f":gray[{measurement_time}]", value=f'{get_transformed_value(sensor["type"], value)}',delta_color="off")

        command_manager(cont_col2, sensor, value)

    pp = cont.popover(label='Details')
    pp.subheader(f'Sensor Details', divider='grey')
    pp.markdown(f"**Serial**: `{sensor['serial']}`")
    pp.markdown(f"**Model**: `{sensor['model']}`")
    pp.markdown(f"**Description**:")
    pp.caption(f"{sensor['description']}")
    pp.subheader(f'Device Details', divider='grey')
    pp.markdown(f"**Serial**: `{sensor['device']['serial']}`")
    pp.markdown(f"**Model**: `{sensor['device']['model']}`")





