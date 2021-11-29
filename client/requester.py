from typing import Dict
import requests


# Should be defined inside the library and changed if ever the 2D simulator is run on another host
url = 'http://127.0.0.1:5000'

open_session = url + '/open-session'
change_speed = url + '/change-speed'
agents_name =  url + '/agents'


def set_speed(agent_name, speed):
    assert 'left' in speed.keys() and 'right' in speed.keys()
    resp = requests.post(change_speed, json={'name': agent_name, "speed": speed})
    return resp

def start_simulator(nb_agent=1):
    resp = requests.get(open_session, json={'nb_agent': nb_agent})
    return resp

def get_agents_name():
    resp = requests.get(agents_name)
    if(resp.status_code == 200):
        return resp.json()['data']
    else: return resp