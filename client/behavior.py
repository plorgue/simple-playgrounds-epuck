from threading import Thread as ParralelClass, Event
from numpy import array, average
from random import choice
from time import time


class Routine(ParralelClass):

    def __init__(self, object_with_io, callback, condition, freq, **callback_kwargs):
        ParralelClass.__init__(self)
        self.period = 1. / freq
        self.object_with_io = object_with_io
        self.callback = callback
        self.callback_kwargs = callback_kwargs

        self.condition = condition
        self._running = Event()
        self._running.clear()
        self._to_terminate = Event()
        self._to_terminate.clear()
        self.verbose = False


class Behavior(Routine):

    def __init__(self, robot, callback, condition, freq):
        Routine.__init__(self, robot, callback, condition, freq)
        self.robot = self.object_with_io
        self.left_wheel = 0.
        self.right_wheel = 0.
        self.activation = 0.

    def loop_core(self):
        res = self.callback(self.robot)
        if len(res) == 2:
            self.left_wheel, self.right_wheel = res
            self.activation = 1.
        else:
            self.left_wheel, self.right_wheel, self.activation = res


class BehaviorMixer(ParralelClass):
    def __init__(self, robot):
        ParralelClass.__init__(self)
        self.period = 1. / robot.freq
        self.robot = robot
        self.behaviors = robot._behaviors
        self.condition = robot.condition
        self._running = Event()
        self._running.clear()
        self._to_terminate = Event()
        self._to_terminate.clear()
        self.mode = "average"

    def run(self):
        while True:
            if self._to_terminate.is_set():
                break
            start_time = time()
            if self._running.is_set():
                self.condition.acquire()
                if not self.behaviors:
                    activations = 0., 0.
                else:
                    if self.mode == "random":
                        activations = self._random()
                    elif self.mode == "average":
                        activations = self._average()
                    else:
                        print(
                            self.mode, "is not a valid mode. Choices are \"random\" or \"average\"")
                self.robot.left_wheel, self.robot.right_wheel = activations
                self.condition.release()
            self.robot.wait(self.period + start_time - time())

    def _average(self):
        activations = array([(b.left_wheel, b.right_wheel, b.activation)
                             for b in self.behaviors.values()])
        activations = average(
            activations[:, :2], weights=activations[:, 2] + 1e-10, axis=0)
        return activations

    def _random(self):
        beh = choice(list(self.behaviors.values()))
        return beh.left_wheel, beh.right_wheel

    def set_mode(self, mode):
        self.condition.acquire()
        self.mode = mode
        self.condition.release()

    def execute(self):
        self._running.set()

    def is_executed(self):
        return self._running.is_set()

    def stop(self):
        self._running.clear()

    def _terminate(self):
        self.stop()
        self._to_terminate.set()
