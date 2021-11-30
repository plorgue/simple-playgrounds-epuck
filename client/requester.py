from typing import Dict
import requests


# Should be defined inside the library and changed if ever the 2D simulator is run on another host
url = 'http://127.0.0.1:5000'

open_session = url + '/open-session'
change_speed = url + '/change-speed'
agents_name =  url + '/agents'
agent_by_name =  url + '/agent'
url_agent_sensor_by_name = lambda name, sensor_name: f'{url}/agent/{name}/sensor/{sensor_name}'
stop_session = url + '/stop-session'
reset_session = url + '/reset-session'

def set_speed(agent_name, speed):
    assert 'left' in speed.keys() and 'right' in speed.keys()
    resp = requests.post(change_speed, json={'name': agent_name, "speed": speed})
    return resp

def start_simulator(nb_agent=1, sensor=None):
    resp = requests.get(open_session, json={'nb_agent': nb_agent, 'sensor': sensor})
    return resp

def get_agents_name():
    resp = requests.get(agents_name)
    if(resp.status_code == 200):
        return resp.json()['data']
    else: return resp

def get_agent_by_name(name):
    resp = requests.get(f'{agent_by_name}/{name}')
    if(resp.status_code == 200):
        return resp.json()['data']
    else: return resp

def get_agent_sensor_by_name(name, sensor):
    resp = requests.get(url_agent_sensor_by_name(name, sensor))
    if(resp.status_code == 200):
        return resp.json()['data']
    else: return resp

def stop_simulator():
    resp = requests.post(stop_session)
    return resp

def reset_simulator():
    resp = requests.post(reset_session)
    return resp