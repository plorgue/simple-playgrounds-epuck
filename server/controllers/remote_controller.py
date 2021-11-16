from simple_playgrounds.agents.parts.controllers import Controller

class RemoteController(Controller):
    """
    This controller is used for agent controlled by external client like a remote notebook.
    
    Attributes are modified when a post request is received
    """

    new_speed = 0

    def __init__(self):
        super().__init__()

    def generate_actions(self):

        commands = {}
        
        # Value of all actuators are modified to see behavior when new_speed changes
        for actuator in self.controlled_actuators:
            commands[actuator] = RemoteController.new_speed 

        return commands

