from simple_playgrounds.playground import SingleRoom
from simple_playgrounds.engine import Engine
from simple_playgrounds.agent.agents import BaseAgent, Eye, MobilePlatform
from simple_playgrounds.device.sensors import SemanticCones
from typing import Dict

import math

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

    def start_simulation(self, agents=None):

        if(agents):
            for agent in agents:
                self.add_agent(**agent)

        self.engine = Engine(time_limit=10000, playground=self.playground)
        self.state_simulator = self.STATE_RUNNING
        self.engine.run()
        self.engine.terminate()
        self.state_simulator = self.STATE_STOPPED

    def get_image(self):
        return self.engine.generate_playground_image()

    def add_agent(self, id, position=(80,80), direction=0, radius=12, type="epuck"):
        aController = RemoteController()

        agent = BaseAgent(controller=aController, name=f"{type}__{id}", radius=radius)

        left_eye = Eye(agent.base_platform, angle_offset=-math.pi / 4)
        right_eye = Eye(agent.base_platform, angle_offset=math.pi / 4)

        agent.add_part(left_eye)
        agent.add_part(right_eye)

        left_sensor = SemanticCones(
            name="left",
            anchor=left_eye, 
            fov=90,
            max_range=220,
            n_cone=30,
            rays_per_cone=5,
            normalize=True,
            invisible_elements=agent.parts)
        right_sensor = SemanticCones(
            name="right",
            anchor=right_eye,
            fov=90,
            max_range=220,
            n_cone=30, 
            rays_per_cone=5,
            normalize=True,
            invisible_elements=agent.parts)

        agent.add_sensor(left_sensor)
        agent.add_sensor(right_sensor)

        self.playground.add_agent(agent=agent)
        agent.initial_coordinates = (position, direction)
        self.controllers[agent.name] = aController

    def get_agents_names(self):
        return [agent.name for agent in self.playground.agents]

    # def get_agents_position(self):
    #     return {agent.name: agent.coordinates for agent in self.playground.agents}

    # def get_agents_velocity(self):
    #     print(self.playground.agents[0].velocity)
    #     return {
    #         agent.name: {"velocity": agent.velocity, "rotation": agent.angular_velocity}
    #         for agent in self.playground.agents
    #     }

    # def get_agent_sensors(self, name):
    #     agent: BaseAgent
    #     for agt in self.playground.agents:
    #         if agt.name == name:
    #             agent = agt
    #     return {"agent": name, "sensors": [sensor.name for sensor in agent.sensors]}

    def get_agent_sensors_value(self, agent_name, mode="closest"):
        MODES = ["closest", "all"]
        assert mode in MODES, f"Modes available {MODES[0]} {MODES[1]}"

        for agt in self.playground.agents:
            if agt.name == agent_name:
                agent = agt
        
        sensors = {}
        for sensor in agent.sensors:
            a_sensor = []
            obj_detected = []
            for detection in sensor.sensor_values:
                isagent = isinstance(detection[0], MobilePlatform)

                type = None
                if(isagent):
                    type, id = detection[0].agent.name.split('__')
                else:
                    id = detection[0].name
                
                
                if id not in obj_detected: 
                    a_sensor.append({
                        "isagent": isagent,
                        "type": type,
                        "id": id,
                        "dist": detection[1],
                        "angle": detection[2]
                    })
                    obj_detected.append(id)
                
            sensors[sensor.name] = a_sensor
        
        if mode == "closest":
            closest_sensors = {}
            for name in sensors:
                closest = {'dist':1}
                for detection in sensors[name]:
                    if detection['dist'] <= closest['dist']:
                        closest = detection
                closest_sensors[name] = closest
            return closest_sensors

        if mode == "all":
            return sensors

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
