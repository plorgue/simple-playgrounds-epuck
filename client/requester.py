import requests


# Should be defined inside the library and changed if ever the 2D simulator is run on another host
url = 'http://127.0.0.1:5000'

open_session = url + '/open-session'
change_speed = url + '/change-speed'


def set_speed(speed):
    resp = requests.post(change_speed, data=speed)
    return resp

def start_simulator():
    resp = requests.get(open_session)
    return resp