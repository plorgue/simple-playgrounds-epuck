from copy import copy
from time import sleep

from threading import Condition
from behavior import Behavior, BehaviorMixer


CHANGE_SPEED_URL = 'agent/change-speed'
GET_SENSOR_VALUES_URL = 'agent/prox-activations'


class Agent:

    def __init__(self, simulator, agent_id, agent_type="epuck", freq=10.) -> None:
        self._right_spd = 0.
        self._left_spd = 0.
        self._simulator = simulator
        self.id = agent_id
        self.freq = freq
        self.type = agent_type
        self._no_detection_value = 2000.
        self.max_speed = 10.
        self._behaviors = {}
        self._condition = Condition()
        self._behavior_mixer = BehaviorMixer(self)
        self._behavior_mixer.start()
        self._conditions = {}

    @property
    def left_spd(self):
        return self._left_spd

    @left_spd.setter
    def left_spd(self, value):
        self._left_spd = copy(value)
        self._set_remote_speed()

    @property
    def right_spd(self):
        return self._right_spd

    @right_spd.setter
    def right_spd(self, value):
        self._right_spd = copy(value)
        self._set_remote_speed()

    @property
    def left_wheel(self):
        return self._left_spd / self.max_speed

    @left_wheel.setter
    def left_wheel(self, value):
        self._left_spd = value * self.max_speed

    @property
    def right_wheel(self):
        return self._right_spd / self.max_speed

    @right_wheel.setter
    def right_wheel(self, value):
        self._right_spd = value * self.max_speed
        
    def _set_remote_speed(self):
        self._simulator._send_request(
            'POST',
            CHANGE_SPEED_URL,
            json={
                "agent_id": f"{self.type}__{self.id}",
                "new_speeds": [self.left_wheel, self.right_wheel]
            }
        )

    def _start(self, dictionary, callback):
        if callback not in dictionary:
            print(("Warning: " + callback.__name__ + " is not attached"))
            return False
        else:
            dictionary[callback].execute()
            return True

    def _stop(self, dictionary, callback):
        if callback not in dictionary:
            print(("Warning: " + callback.__name__ + " is not attached"))
            return False
        else:
            dictionary[callback].stop()
            return True

    def _detach(self, dictionary, callback):
        if callback not in dictionary:
            print(("Warning: " + callback.__name__ + " was not attached"))
        else:
            dictionary[callback].stop()
            dictionary[callback]._terminate()
            sleep(dictionary[callback].period)
            del dictionary[callback]

    def _detach_all(self, dictionary):
        # because one can't modify the dict during the loop on itself
        dict_copy = dict(dictionary)
        for callback, item in dict_copy.items():
            self._detach(dictionary, callback)

    def _check(self, dictionary):
        label = "Behavior" if dictionary == self._behaviors else "Routine"
        if not len(dictionary):
            print("No " + label.lower() + " attached")
        for callback, obj in dictionary.items():
            print(label + " \"{name}\" is attached and {started}".format(
                name=callback.__name__, started="STARTED" if obj._running.is_set() else "NOT STARTED."))

    def stop(self):
        self.right_wheel, self.left_wheel = 0., 0.

    def wait(self, seconds):
        sleep(seconds)

    def prox_activations(self, tracked_objects=None): #, return_epucks=False
        sensor = self._simulator._send_request(
            'GET',
            GET_SENSOR_VALUES_URL,
            json={
                "agent_name": f"{self.type}__{self.id}",
            }   
        )
        if sensor.status_code == 200:
            return sensor.json().get('data')


    def attach_behavior(self, callback, freq):
        self._behaviors[callback] = Behavior(self, callback, self._condition, freq)
        self._behaviors[callback].start()

    def start_behavior(self, callback):
        if self._start(self._behaviors, callback):
            if not self._behavior_mixer.is_executed():
                self._behavior_mixer.execute()
            print("Behavior " + callback.__name__ + " started")

    def stop_behavior(self, callback):
        if self._stop(self._behaviors, callback):
            if all([not b.is_executed() for b in self._behaviors.values()]):
                self._behavior_mixer.stop()
            print("Behavior " + callback.__name__ + " stopped")

    def detach_behavior(self, callback):
        self._detach(self._behaviors, callback)
        print("Behavior " + callback.__name__ + " detached")

    def check_behaviors(self):
        self._check(self._behaviors)

    def detach_all_behaviors(self):
        self._detach_all(self._behaviors)
