from simple_playgrounds.agents.parts.controllers import Controller
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.engine import Engine
from simple_playgrounds.agents.agents import BaseAgent
from typing import Dict

from controllers.remote_controller import RemoteController


class SpgService:

    controllers: Dict[str, RemoteController]
    playground: SingleRoom

    def __init__(self):
        # Initialize simple simulator with a room and a base agent
        self.playground = SingleRoom(size=(600, 600))
        self.controllers = {}
        
    def set_speed(self, name, speed):
        """
        name:    agent name
        speed:   {left: float between -1 and 1, right: foat between -1 and 1}
        """
        velocity = (speed['left'] + speed['right'])/2
        rotation = (speed['left'] - speed['right'])/2
        self.controllers[name].velocity = max(min(velocity,1),-1)
        self.controllers[name].rotation_velocity = max(min(rotation,1),-1)

        return velocity, rotation

    def start_simulation(self, nb_agent=1):

        for _ in range(nb_agent):
            aController = RemoteController()
            agent = BaseAgent(controller=aController, radius=10)
            self.playground.add_agent(agent=agent)
            self.controllers[agent.name] = aController

        engine = Engine(time_limit=10000, playground=self.playground, screen=True)
        engine.run(update_screen= True)
        engine.terminate()

    def get_agents_names(self):
        return [agent.name for agent in self.playground.agents]

    def get_agents_position(self):
        return {agent.name: agent.coortinates for agent in self.playground.agents}

    def get_agents_velocity(self):
        return {agent.name: { 'velocity': agent.velocity, 'angular': agent.angular_velocity} for agent in self.playground.agents}

    def get_agents_sensor_value(self):
        pass





    