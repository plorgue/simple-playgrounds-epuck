from simple_playgrounds.agents.parts.controllers import Controller
from simple_playgrounds.agents.parts.actuators import DiscreteActuator, ContinuousActuator 

class RemoteController(Controller):

    new_speed = 0

    def __init__(self):
        super().__init__()

    def generate_actions(self):

        commands = {}
        for actuator in self.controlled_actuators:

            # if isinstance(actuator, DiscreteActuator):
            #     act_value = 

            # elif isinstance(actuator, ContinuousActuator):

            #     if actuator.centered:
            #         act_value = random.choice([-1, 0, 1])
            #     else:
            #         act_value = random.choice([0, 1])

            # else:
            #     raise ValueError("Actuator type not recognized")

            commands[actuator] = RemoteController.new_speed

        return commands

