import time
from copy import copy
from time import sleep

from random import random

from threading import Condition
from behavior import Behavior, BehaviorMixer


CHANGE_SPEED_URL = "agent/change-speed"
GET_SENSOR_VALUES_URL = "agent/prox-activations"


class Agent:
    def __init__(
        self,
        simulator,
        agent_id,
        use_proximeters=list(range(2)),
        agent_type=None,
        initial_coordinates=None,
        radius=None,
        freq=1.0,
    ) -> None:
        self._right_spd = 0.0
        self._left_spd = 0.0
        self._simulator = simulator
        self.id = agent_id
        self.freq = freq
        self.type = agent_type if agent_type is not None else "epuck"
        self.initial_coordinates = (
            initial_coordinates
            if initial_coordinates is not None
            else (
                (random(), random()),
                random(),
            )
        )
        self.radius = radius if radius is not None else 12
        self._no_detection_value = 2000.0
        self.max_speed = 10.0
        self._behaviors = {}
        self._condition = Condition()
        self._behavior_mixer = BehaviorMixer(self)
        self._behavior_mixer.start()
        self._conditions = {}
        self.used_proximeters = use_proximeters

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
        self._left_spd = copy(value * self.max_speed)
        self._set_remote_speed()

    @property
    def right_wheel(self):
        return self._right_spd / self.max_speed

    @right_wheel.setter
    def right_wheel(self, value):
        self._right_spd = copy(value * self.max_speed)
        self._set_remote_speed()

    def _set_remote_speed(self):
        self._simulator._send_request(
            "POST",
            CHANGE_SPEED_URL,
            json={
                "agent_id": f"{self.type}__{self.id}",
                "new_speeds": [self.left_wheel, self.right_wheel],
            },
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
            print(
                label
                + ' "{name}" is attached and {started}'.format(
                    name=callback.__name__,
                    started="STARTED" if obj._running.is_set() else "NOT STARTED.",
                )
            )

    def stop(self):
        self.right_wheel, self.left_wheel = 0.0, 0.0

    def wait(self, seconds):
        start = time.time()
        while time.time() - start < seconds:
            sleep(0.005)

    def prox_activations(self, tracked_objects=None, return_epucks=False):
        response = self._simulator._send_request(
            "GET",
            GET_SENSOR_VALUES_URL,
            json={
                "agent_name": f"{self.type}__{self.id}",
            },
        )
        if response.status_code == 200:
            proximeters = response.json()
            activations = [1, 1]
            if tracked_objects is not None:
                activations = [
                    prox.get("dist", 1) if prox.get("type", None) in tracked_objects
                    # and prox.get("type", None) not in excluded_objects
                    else 1
                    for prox in proximeters.values()
                ]
            else:
                activations = [
                    prox.get("dist", 1)
                    # if prox.get("type", None) not in excluded_objects
                    # else 1
                    for prox in proximeters.values()
                ]
            if return_epucks:
                return (
                    *activations,
                    *[prox.get("type", None) for prox in proximeters.values()],
                )
            else:
                return activations
        else:
            raise Exception("Could not get activations")

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
