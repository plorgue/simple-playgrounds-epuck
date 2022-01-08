from typing import Dict

import cv2
import math
import time
from simple_playgrounds.agent.agents import BaseAgent, Eye, MobilePlatform
from simple_playgrounds.device.sensors import SemanticCones
from simple_playgrounds.engine import Engine
from simple_playgrounds.playground import SingleRoom
from simple_playgrounds.element.elements.edible import Apple

from controllers.remote_controller import RemoteController


class SpgService:
    STATE_RUNNING = "running"
    STATE_STOPPED = "stop"
    STATE_WAITING = "waiting"

    controllers: Dict[str, RemoteController]
    playground: SingleRoom
    state_simulator: str
    engine: Engine

    done = False

    def __init__(self):
        # Initialize simple simulator with a room and a base agent
        self.playground = SingleRoom(size=(500, 500))
        self.controllers = {}
        self.state_simulator = self.STATE_STOPPED

    def start_simulation(self, agents=None, playground=None, show_image=True):
        if playground is None:
            playground = {"size": (600, 600)}
        if self.state_simulator != self.STATE_RUNNING:

            self.playground = SingleRoom(size=playground["size"])

            if agents:
                for agent in agents:
                    self.add_agent(**agent)

            self.engine = Engine(time_limit=10000, playground=self.playground)
            self.state_simulator = self.STATE_RUNNING
            if show_image:
                self.done = False
                while not self.done:
                    actions = {}
                    for agent in self.playground.agents:
                        actions[agent] = agent.controller.generate_actions()
                    self.engine.step(actions)
                    self.engine.update_observations()

                    cv2.imshow('playground', self.get_image()[:, :, ::-1])

                    if cv2.waitKey(1) in (113, 27):
                        self.done = True

                    time.sleep(0.05)
                cv2.destroyWindow('playground')
                cv2.waitKey(1)
            else:
                self.engine.run()
            self.engine.terminate()
            self.state_simulator = self.STATE_STOPPED
            return True
        return False

    def get_image(self):
        return self.engine.generate_playground_image()

    def get_simulator_state(self):
        return self.state_simulator

    def stop_simulator(self):
        self.done = True
        self.playground.done = True
        self.state_simulator = self.STATE_WAITING

    def reset_simulator(self):
        self.playground.reset()
        self.playground = SingleRoom(size=(600, 600))
        self.controllers = {}
        self.engine.terminate()
        self.state_simulator = self.STATE_STOPPED

    def add_agent(
            self,
            id,
            initial_coordinates=((0.5, 0.5), 0),
            radius=12,
            type="epuck"
    ):
        """
        Add an BaseAgent with 2 sensors SemanticCones attached to 2 eyes
        SemanticCones detect object over 180 degrees in front of the agent.
        The left sensor covers 90° on the front left and the right sensor 90° on the front right

        Args:
            id: String
            initial_coordinates: Tuple((normalized position), orientation radian)
            radius: Integer
            type: String
        """

        a_controller = RemoteController()
        agent = BaseAgent(controller=a_controller, name=f"{type}_{id}", radius=radius)
        self.controllers[agent.name] = a_controller

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
            invisible_elements=agent.parts,
        )
        right_sensor = SemanticCones(
            name="right",
            anchor=right_eye,
            fov=90,
            max_range=220,
            n_cone=30,
            rays_per_cone=5,
            normalize=True,
            invisible_elements=agent.parts,
        )

        agent.add_sensor(left_sensor)
        agent.add_sensor(right_sensor)

        self.playground.add_agent(agent=agent)

        if initial_coordinates[0][0] > 1 or initial_coordinates[0][1] > 1:
            # position not normalized
            agent.initial_coordinates = initial_coordinates
        else:
            agent.initial_coordinates = (
                (
                    int(initial_coordinates[0][0] * self.playground.size[0]),
                    int(initial_coordinates[0][1] * self.playground.size[1]),
                ),
                initial_coordinates[1],
            )

    def get_agents_names(self):
        return [agent.name for agent in self.playground.agents]

    def get_agent_sensors_value(self, agent_name, mode="closest"):
        modes = ["closest", "all"]
        assert mode in modes, f"Modes available {modes[0]} {modes[1]}"

        agent = None
        for agt in self.playground.agents:
            if agt.name == agent_name:
                agent = agt

        if agent is None:
            raise ValueError(f"no agent with name {agent} was found")

        sensors = {}
        for sensor in agent.observations.keys():
            a_sensor = []
            obj_detected = []
            for detection in agent.observations[sensor]:
                agent_type, agent_id = None, None
                name = detection[0].name.split("_")

                if len(name) == 1:
                    agent_id = name[0]
                elif len(name) == 2:
                    agent_type, agent_id = name

                if agent_id not in obj_detected:
                    a_sensor.append(
                        {
                            "is_robot": isinstance(detection[0], MobilePlatform),
                            "type": agent_type,
                            "id": agent_id,
                            "dist": detection[1],
                            "angle": detection[2],
                        }
                    )
                    obj_detected.append(agent_id)

            sensors[sensor.name] = a_sensor
        if mode == "closest":
            closest_sensors = {}
            for name in sensors:
                if len(sensors[name]) > 0:
                    closest = {"dist": 1}
                    for detection in sensors[name]:
                        if detection["dist"] <= closest["dist"]:
                            closest = detection
                    closest_sensors[name] = closest
                else:
                    closest_sensors[name] = {}
            return closest_sensors

        if mode == "all":
            print(sensors)
            return sensors

    def set_speed(self, name, speed):
        """
        name:    agent name
        speed:   {left: float between -1 and 1, right: float between -1 and 1}
        """
        velocity = (speed["left"] + speed["right"]) / 2
        rotation = (speed["left"] - speed["right"]) / 2
        self.controllers[name].velocity = max(min(velocity, 1), -1)
        self.controllers[name].rotation_velocity = max(min(rotation, 1), -1)

        return velocity, rotation

    def add_sphere(self, name, position, sizes, mass, eatable):
        radius = sum(sizes) / len(sizes)  # Let's just stick to a circle shape for now
        if eatable:
            sphere = Apple(1.0, 1.0, 0.9, name=name, mass=mass, radius=radius)
        else:
            raise NotImplementedError("functionality add_sphere not implemented for non edible elements")
        self.playground.add_element(sphere, initial_coordinates=(tuple(position), 0))



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
