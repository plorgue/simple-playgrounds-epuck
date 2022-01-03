"""
Script for debug
"""

import requests

# Should be defined inside the library and changed if ever the 2D simulator is run on another host
url = 'http://127.0.0.1:5000'

open_session = url + '/open-session'
change_speed = url + '/change-speed'
agents_name = url + '/agents'
agent_by_name = url + '/agent'


def url_agent_sensor_by_name(
        name, sensor_name): return f'{url}/agent/{name}/sensor/{sensor_name}'


stop_session = url + '/stop-session'
reset_session = url + '/reset-session'


def set_speed(data):
    assert len(data.keys()) == 2, "Invalid arguments"
    assert "agent_id" in data.keys(), "Invalid arguments"
    assert "new_speeds" in data.keys(), "Invalid arguments"
    assert type(data["new_speeds"]) == list and len(data["new_speeds"]) == 2
    response = requests.post(change_speed, json=data)
    return response


def start_simulator():
    data = {
        "agents": [
            {
                "id": 0,
                "type": "epuck",
                "initial_coordinates": [[0.5, 0.5], 0],
                "radius": 15
            }
        ]
    }
    resp = requests.get(open_session, json=data)
    return resp


def get_agents_name():
    resp = requests.get(agents_name)
    if resp.status_code == 200:
        return resp.json()['data']
    else:
        return resp


def get_agent_by_name(name):
    resp = requests.get(f'{agent_by_name}/{name}')
    if resp.status_code == 200:
        return resp.json()['data']
    else:
        return resp


def get_agent_sensor_by_name(name, sensor):
    resp = requests.get(url_agent_sensor_by_name(name, sensor))
    if resp.status_code == 200:
        return resp.json()['data']
    else:
        return resp


def stop_simulator():
    resp = requests.post(stop_session)
    return resp


def reset_simulator():
    resp = requests.post(reset_session)
    return resp
