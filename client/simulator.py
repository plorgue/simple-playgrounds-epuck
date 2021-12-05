
from urllib import parse
import requests
from requests.sessions import InvalidSchema, session
from agent import Agent


OPEN_SESSION_URL = 'open-session'
CLOSE_SESSION_URL = 'close-session'
RESET_SIMULATOR_URL = 'reset-simulator'


def get_session(n_agents=1, old_simulator=None):
    if old_simulator is not None:
        old_simulator.stop()
        del old_simulator

    simulator = Simulator()
    agents = [simulator.create_agent() for _ in range(n_agents)]

    try:
        simulator.start()
    except InvalidSchema:
        raise Exception(
            "Could not reach the server. Are you sure the simulator is running ?"
        ) from None

    if n_agents == 1:
        return simulator, agents[0]
    else:
        return [simulator] + agents


def close_session(simulator):
    simulator.stop()
    for agent in simulator._agents:
        del agent
    del simulator


class Simulator:

    def __init__(self, host='127.0.0.1', port=5000) -> None:
        self._agents = []
        self._session = requests.Session()
        self._url = ''.join(('http://', host, ':', str(port), '/'))
        self._allowed_request_methods = ('POST', 'GET', 'DELETE', 'PUT')

    def create_agent(self):
        agent = Agent(self, 123)
        self._agents.append(agent)
        return agent

    def _send_request(self, method, type, **kwargs):
        if method not in self._allowed_request_methods:
            raise ValueError(f"The request should have a valid method")
        self._session.request(method, ''.join(
            (self._url, type)), params=kwargs)

    def start(self):
        json_data = {
            'agents': {
                agent._id: [None] for agent in self._agents
            },
            'nb_agents': len(self._agents)

        }

        resp = self._send_request('POST', OPEN_SESSION_URL, json=json_data)
        return resp

    def reset(self):
        self._send_request('POST', RESET_SIMULATOR_URL)

    def stop(self) -> None:
        self._send_request('POST', CLOSE_SESSION_URL)
        self._session.close()
