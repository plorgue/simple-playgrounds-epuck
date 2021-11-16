from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.engine import Engine
from simple_playgrounds.agents.agents import BaseAgent

from controllers.remote_controller import RemoteController


class SpgService:

    agent: BaseAgent
    playground: SingleRoom

    def __init__(self):
        # Initialize simple simulator with a room and a base agent
        self.playground = SingleRoom(size=(300, 300))
        self.agent = BaseAgent(controller=RemoteController(), radius=15)
        self.playground.add_agent(agent=self.agent)
        
    def set_speed(self, speed):
        RemoteController.new_speed = speed

    def start_simulation(self):
        engine = Engine(time_limit=10000, playground=self.playground, screen=True)
        engine.run(update_screen= True)
        engine.terminate()





    