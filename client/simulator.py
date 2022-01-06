import random
from flask.wrappers import Response

import requests
from agent import Agent


OPEN_SESSION_URL = "simulator/open"
CLOSE_SESSION_URL = "simulator/close"
RESET_SIMULATOR_URL = "simulator/reset"
STATE_SIMULATOR = "simulator"


def get_session(nb_agents=1, old_simulator=None, agent_types=[]):
    if old_simulator is not None:
        old_simulator.stop()
        del old_simulator

    simulator = Simulator()

    agents = []
    for agent_id in range(nb_agents):
        if agent_id < len(agent_types):
            agents.append(
                simulator.create_agent(agent_id=agent_id, type=agent_types[agent_id])
            )
        else:
            agents.append(simulator.create_agent(agent_id=agent_id))

    try:
        response = simulator.start()
        assert response.status_code == 200
    except Exception as e:
        raise Exception(
            f"Encountered an exception while trying to start the simulator. Are you sure the server is running?\n {e}"
        ) from None

    if nb_agents == 1:
        return simulator, agents[0]
    else:
        # noinspection PyTypeChecker
        return [simulator] + agents


def close_session(simulator):
    simulator.stop()
    simulator.agents.clear()
    del simulator


class Simulator:
    def __init__(self, host="127.0.0.1", port=5000) -> None:
        self.agents = []
        self._session = requests.Session()
        # noinspection PyTypeChecker
        self._url = "".join(("http://", host, ":", str(port), "/"))
        self._allowed_request_methods = ("POST", "GET", "DELETE", "PUT")

    def create_agent(self, agent_id, type):
        agent = Agent(self, agent_id=agent_id, agent_type=type)
        self.agents.append(agent)
        return agent

    def _send_request(self, method, request_type, **kwargs) -> Response:
        if method not in self._allowed_request_methods:
            raise ValueError(f"The request should have a valid method")
        return self._session.request(
            method, "".join((self._url, request_type)), json=kwargs
        )

    def start(self):
        data = {
            "agents": [
                {
                    "id": agent.id,
                    "type": agent.type,
                    "initial_coordinates": [
                        [random.random(), random.random()],
                        random.random(),
                    ],
                    "radius": 10
                    # "used_proximeters": agent.used_proximeters,
                }
                for agent in self.agents
            ]
        }

        resp = self._send_request("GET", OPEN_SESSION_URL, json=data)
        return resp

    def status(self):
        resp = self._send_request("GET", STATE_SIMULATOR)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("status", None)
        return None

    def reset(self) -> None:
        self._send_request("POST", RESET_SIMULATOR_URL)

    def stop(self) -> None:
        self._send_request("POST", CLOSE_SESSION_URL)
        self._session.close()
