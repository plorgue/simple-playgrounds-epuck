from os import name
from re import I
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.engine import Engine
from simple_playgrounds.agents.agents import HeadAgent
from simple_playgrounds.agents.sensors.semantic_sensors import SemanticCones
from simple_playgrounds.agents.sensors.sensor import Sensor
from typing import Dict

from controllers.remote_controller import RemoteController
class SpgService:

    STATE_RUNNING = "running"
    STATE_STOPPED = "stop"
    STATE_WAITING = "waiting"

    controllers: Dict[str, RemoteController]
    playground: SingleRoom
    state_simulator: str
    engine: Engine

    def __init__(self):
        # Initialize simple simulator with a room and a base agent
        self.playground = SingleRoom(size=(600, 600))
        self.controllers = {}
        self.state_simulator = self.STATE_STOPPED

    def set_speed(self, name, speed):
        """
        name:    agent name
        speed:   {left: float between -1 and 1, right: foat between -1 and 1}
        """
        velocity = (speed["left"] + speed["right"]) / 2
        rotation = (speed["left"] - speed["right"]) / 2
        self.controllers[name].velocity = max(min(velocity, 1), -1)
        self.controllers[name].rotation_velocity = max(min(rotation, 1), -1)

        return velocity, rotation

    def start_simulation(self, nb_agent=1, sensor=None, ids=[]):

        self.add_agents(nb_agent=nb_agent, sensor=sensor, ids=ids)

        self.engine = Engine(time_limit=10000, playground=self.playground, screen=True)
        self.state_simulator = self.STATE_RUNNING
        self.engine.run(update_screen=True)
        self.engine.terminate()
        self.state_simulator = self.STATE_STOPPED

    def add_agents(self, nb_agent=1, sensor=None, ids=[]):
        if len(ids) > 0:
            nb_agent = len(ids)

        for i in range(nb_agent):
            aController = RemoteController()
            if len(ids) > 0:
                agent = HeadAgent(controller=aController, radius=10, name=ids[i])
            else:
                agent = HeadAgent(controller=aController, radius=10)
            if sensor == "proximiter":
                agent.add_sensor(
                    SemanticCones(anchor=agent.head, invisible_elements=agent.parts)
                )
            self.playground.add_agent(agent=agent)
            self.controllers[agent.name] = aController

    def get_agents_names(self):
        # agents = [agent.name for agent in self.playground.agents]
        # sensor_name = self.get_agent_sensors(name=agents[0])
        # print(sensor_name)
        # print(self.get_agent_sensor_value(sensor_name[0]))
        return [agent.name for agent in self.playground.agents]

    def get_agents_position(self):
        return {agent.name: agent.coordinates for agent in self.playground.agents}

    def get_agents_velocity(self):
        print(self.playground.agents[0].velocity)
        return {
            agent.name: {"velocity": agent.velocity, "rotation": agent.angular_velocity}
            for agent in self.playground.agents
        }

    def get_agent_sensors(self, name):
        agent: HeadAgent
        for agt in self.playground.agents:
            if agt.name == name:
                agent = agt
        return {"agent": name, "sensors": [sensor.name for sensor in agent.sensors]}

    def get_agent_sensor_value(self, name, sensor_name):
        sensor: Sensor
        for agt in self.playground.agents:
            if agt.name == name:
                for ssor in agt.sensors:
                    if ssor.name == sensor_name:
                        sensor = ssor
        print(sensor.sensor_values)
        detections = [ {"obj": type(detection[0]).__name__, 'dist': detection[1], 'angle': detection[2]}for detection in sensor.sensor_values]
        print(detections)
        return {
            "agent": name,
            "sensor": sensor_name,
            "value": detections

            # "distances": {"object_1": 21.7, "agent_2": 13.8},
        }

    def get_simulator_state(self):
        return self.state_simulator

    def stop_simulator(self):
        self.playground.done = True
        self.state_simulator = self.STATE_WAITING

    def reset_simulator(self):
        self.playground.reset()
        self.playground = SingleRoom(size=(600, 600))
        self.controllers = {}
        self.engine.terminate()
        self.state_simulator = self.STATE_STOPPED
