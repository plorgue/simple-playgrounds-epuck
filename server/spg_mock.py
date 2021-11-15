from simple_playgrounds.agents.parts.controllers import Controller, Keyboard
from simple_playgrounds.playgrounds.layouts import SingleRoom
from simple_playgrounds.engine import Engine
from simple_playgrounds.agents.agents import BaseAgent

import threading
# import asyncio

from controllers.remote_controller import RemoteController


class SpgMock:

    agent: BaseAgent
    playground: SingleRoom

    def __init__(self):
        self.playground = SingleRoom(size=(150, 100))
        self.agent = BaseAgent(controller=RemoteController(), radius=10)
        self.playground.add_agent(self.agent)
        
    def get_simulator(self):
        pass

    def get_agent(self):
        pass

    def get_observation(self, agent_id):
        pass
    
    def set_speed(self, speed):
        RemoteController.new_speed = speed
    
    # def _run_engine(self, engine):

    def start_simulation(self):
        engine = Engine(time_limit=10000, playground=self.playground, screen=True)
        engine.run(update_screen= True)
        engine.terminate()
        # simu_thread = threading.Thread(target=self._run_engine, args=(engine,))
        # simu_thread.start()
        # self._run_engine(engine)
        # task = asyncio.create_task(self._run_engine(engine))
        # return (self.playground, self.agent)





    