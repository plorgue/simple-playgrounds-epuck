from simple_playgrounds.agent.controllers import Controller
from simple_playgrounds.agent.actuators import LongitudinalForce, AngularVelocity


class RemoteController(Controller):
    """
    This controller is used for agent controlled by external client like a remote notebook.
    
    Attributes are modified when a post request is received
    """

    def __init__(self):
        super().__init__()
        self._velocity = 0
        self._rotation = 0

    def generate_actions(self):

        commands = {}

        for actuator in self.controlled_actuators:
            if isinstance(actuator, LongitudinalForce):
                commands[actuator] = self._velocity
            elif isinstance(actuator, AngularVelocity):
                commands[actuator] = self._rotation

        return commands

    @property
    def velocity(self):
        return self._velocity

    @property
    def rotation_velocity(self):
        return self._rotation

    @velocity.setter
    def velocity(self, new_velocity):
        self._velocity = new_velocity

    @rotation_velocity.setter
    def rotation_velocity(self, new_rotation):
        self._rotation = new_rotation

    def terminates_episode(self):
        pass
