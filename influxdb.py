import os
from datetime import datetime

import streamlit as st
from influxdb_client import InfluxDBClient

ORG = os.getenv('DOCKER_INFLUXDB_INIT_ORG')
BUCKET = os.getenv('DOCKER_INFLUXDB_INIT_BUCKET')
TOKEN = os.getenv('DOCKER_INFLUXDB_INIT_ADMIN_TOKEN')


@st.cache_data
def connect_to_influxdb():
    return InfluxDBClient(
        url=f'{os.getenv("DOCKER_INFLUXDB_HOST_TYPE")}://{os.getenv("DOCKER_INFLUXDB_HOST")}:{os.getenv("DOCKER_INFLUXDB_PORT")}',
        token=TOKEN,
        org=ORG)


client = connect_to_influxdb()


def get_device_data(client, device_serial, start_range):
    """
    Query data and return a Pandas DataFrame
    """
    query_api = client.query_api()

    # last value
    result_df = query_api.query_data_frame(f'from(bucket: "{BUCKET}") '
                                           f'|> range(start: {start_range}) '
                                           '|> timeShift(duration: 3h) '
                                           f'|> filter(fn: (r) => r["_measurement"] == "device_status") '
                                           f'|> filter(fn: (r) => r["device_serial"] == "{device_serial}") '
                                           '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                           '|> keep(columns: ["_time", "device_serial", "status"])'
                                           )
    if not result_df.empty:
        result_df = result_df.drop(['result', 'table'], axis=1)
        result_df = result_df.sort_values(by='_time', ascending=False)
    return result_df


def get_sensor_data(client, selected_sensor_serial, start_range, window_range, map_function=None):
    """
    Query data and return a Pandas DataFrame
    """
    query_api = client.query_api()

    result_df = query_api.query_data_frame(f'from(bucket: "{BUCKET}") '
                                           f'|> range(start: {start_range}) '
                                           '|> timeShift(duration: 3h) '
                                           f'|> filter(fn: (r) => r["_measurement"] == "sensor_data") '
                                           f'|> filter(fn: (r) => r["sensor_serial"] == "{selected_sensor_serial}") '
                                        #    f'|> aggregateWindow(every: {window_range}, fn: mean, createEmpty: true)'
                                           # '|> yield(name: "mean") '
                                           '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                           '|> keep(columns: ["_time", "data", "unit"])'
                                           f'{map_function if map_function else ""}'
                                           # '|> map(fn: (r) => ({ r with data: (r.data / 500) * 100 }))'
                                           )
    return result_df


def get_device_status(device_serial):
    """
    Query data and return a Pandas DataFrame
    """
    query_api = client.query_api()

    result = query_api.query(f'from(bucket: "{BUCKET}") '
                             f'|> range(start: -10s) '
                             '|> timeShift(duration: 3h) '
                             f'|> filter(fn: (r) => r["_measurement"] == "device_status") '
                             f'|> filter(fn: (r) => r["device_serial"] == "{device_serial}") '
                             '|> last()')
    device_status = None

    for table in result:
        for record in table.records:
            device_status = record.get_value()
    return device_status


def get_last_value(sensor_serial):
    """
    Query data and return a Pandas DataFrame
    """
    query_api = client.query_api()

    result = query_api.query(f'from(bucket: "{BUCKET}") '
                             f'|> range(start: -1h) '
                             '|> timeShift(duration: 3h) '
                             f'|> filter(fn: (r) => r["_measurement"] == "sensor_data") '
                             f'|> filter(fn: (r) => r["sensor_serial"] == "{sensor_serial}") '
                             '|> last()')
    last_value = None
    measurement_time = None
    for table in result:
        for record in table.records:
            last_value = record.get_value()
            measurement_time = record.get_time()
    # Convert string to datetime object
    if measurement_time:
        dt = datetime.fromisoformat(str(measurement_time))

        # Format datetime object to a more readable format
        measurement_time = dt.strftime("%B %d, %Y, %I:%M:%S %p %Z")
    return last_value, measurement_time
