import requests
import time
from threading import Condition
import numpy as np

from flask.wrappers import Response
from agent import Agent
from behavior import Routine, RoutineManager


OPEN_SESSION_URL = "simulator/open"
CLOSE_SESSION_URL = "simulator/close"
RESET_SIMULATOR_URL = "simulator/reset"
ADD_SPHERE_URL = "simulator/add-sphere"
STATE_SIMULATOR = "simulator"


def get_session(nb_agents=1, old_simulator=None, agents=None, **args):
    if agents is None:
        agents = []
    if old_simulator is not None:
        old_simulator.stop()
        del old_simulator

    simulator = Simulator(**args)

    agents_created = []
    for agent_id in range(nb_agents):
        arg = {}
        if agent_id < len(agents):
            arg = agents[agent_id]
        agents_created.append(simulator.create_agent(agent_id=agent_id, **arg))

    try:
        response = simulator.start()
        assert response.status_code == 200
    except Exception as e:
        raise Exception(
            f"Encountered an exception while trying to start the simulator. Are you sure the server is running?\n {e}"
        ) from None

    if nb_agents == 1:
        return simulator, agents_created[0]
    else:
        # noinspection PyTypeChecker
        return [simulator] + agents_created


def close_session(simulator):
    simulator.stop()
    simulator.agents.clear()
    del simulator


def sphere_apparition(simulator, sizes=None, mass=0.5, eatable=True, max_pos=None, min_pos=None):
    if simulator.n_spheres is None:
        simulator.n_spheres = 0
    if sizes is None:
        sizes = [0.01, 0.01]
    if max_pos is None:
        max_pos = [1.0, 1.0]
    if min_pos is None:
        min_pos = [0.0, 0.0]

    max_pos = np.array(max_pos)
    min_pos = np.array(min_pos)

    position = np.random.rand(2) * (max_pos - min_pos) + min_pos
    name = "Sphere_" + str(simulator.n_spheres + 1)
    simulator._send_request(
        "POST",
        ADD_SPHERE_URL,
        json={
            "name": name,
            "position": position.tolist(),
            "sizes": sizes,
            "mass": mass,
            "eatable": eatable
        }
    )
    simulator.n_spheres += 1

class Simulator:
    def __init__(self, host="127.0.0.1", port=5000, playground_params = {}) -> None:
        self.agents = []
        self.playground_params = playground_params
        self._session = requests.Session()
        # noinspection PyTypeChecker
        self._url = "".join(("http://", host, ":", str(port), "/"))
        self._allowed_request_methods = ("POST", "GET", "DELETE", "PUT")
        self.eatable_objects = None
        self.n_spheres = None
        self._condition = Condition()
        self.routine_manager = RoutineManager()

    def start(self):
        agents = []
        for agent in self.agents:
            agent_params = {
                    "id": agent.id,
                    "type": agent.type,
                    "initial_coordinates": agent.initial_coordinates,
                    "radius": agent.radius,
                }
            if agent.texture is not None:
                agent_params["texture"] = agent.texture
            agents.append(agent_params)

        data = {
            "agents": 
                agents,
            "playground":{
                **self.playground_params
            }
        }
        resp = self._send_request("GET", OPEN_SESSION_URL, json=data)
        return resp

    def status(self):
        resp = self._send_request("GET", STATE_SIMULATOR)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("status", None)
        return None

    def wait(self, seconds):
        start = time.time()
        while time.time() - start < seconds:
            time.sleep(0.005)

    def reset(self) -> None:
        self._send_request("POST", RESET_SIMULATOR_URL)

    def stop(self) -> None:
        self._send_request("POST", CLOSE_SESSION_URL)
        self._session.close()

    def _send_request(self, method, request_type, **kwargs) -> Response:
        if method not in self._allowed_request_methods:
            raise ValueError(f"The request should have a valid method")
        return self._session.request(
            method, "".join((self._url, request_type)), json=kwargs
        )

    def create_agent(self, agent_id, **kwargs):
        agent = Agent(self, agent_id=agent_id, **kwargs)
        self.agents.append(agent)
        return agent

    def start_sphere_apparition(self, period=3., min_pos=None, max_pos=None):
        self.attach_routine(sphere_apparition, freq=1.0 / period, max_pos=max_pos, min_pos=min_pos)
        # self.attach_routine(eating, freq=4.)
        self.start_routine(sphere_apparition)
        # self.start_routine(eating)

    def stop_sphere_apparition(self):
        self.stop_routine(sphere_apparition)
        # self.stop_routine(eating)

    def attach_routine(self, callback, freq, **kwargs):
        routine = Routine(self, callback, self._condition, freq, **kwargs)
        self.routine_manager.attach(routine)

    def detach_routine(self, callback):
        self.routine_manager.detach(callback)
        print("Routine " + callback.__name__ + " detached")

    def detach_all_routines(self):
        self.routine_manager.detach_all()

    def start_routine(self, callback):
        if self.routine_manager.start(callback):
            print("Routine " + callback.__name__ + " started")

    def start_all_routines(self):
        self.routine_manager.start_all()

    def stop_routine(self, callback):
        if self.routine_manager.stop(callback):
            print("Routine " + callback.__name__ + " stopped")

    def stop_all_routines(self):
        self.routine_manager.stop_all()

    def check_routines(self):
        self.routine_manager.check()
