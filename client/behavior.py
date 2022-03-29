from threading import Thread as ParallelClass, Event
from numpy import array, average
from random import choice
from time import time, sleep


class Routine(ParallelClass):
    def __init__(
            self,
            agent,
            callback,
            condition,
            freq,
            **callback_kwargs
    ):
        ParallelClass.__init__(self)
        self.period = 1.0 / freq
        self.agent = agent
        self.callback = callback
        self.callback_kwargs = callback_kwargs

        self.condition = condition
        self._running = Event()
        self._running.clear()
        self._to_terminate = Event()
        self._to_terminate.clear()
        self.verbose = False

    def run(self):
        while True:
            if self._to_terminate.is_set():
                break
            start_time = time()
            if self._running.is_set():
                self.condition.acquire()
                self.loop_core()
                self.condition.release()
            time_to_wait = self.period + start_time - time()
            if time_to_wait >= 0.0:
                self.agent.wait(time_to_wait)
            elif self.verbose:
                print("Too slow")

    def loop_core(self):
        self.callback(self.agent, **self.callback_kwargs)

    def execute(self):
        self._running.set()

    def is_executed(self):
        return self._running.is_set()

    def stop(self):
        self._running.clear()

    def _terminate(self):
        self._to_terminate.set()


class Behavior(Routine):
    def __init__(
            self,
            robot,
            callback,
            condition,
            freq
    ):
        Routine.__init__(self, robot, callback, condition, freq)
        self.robot = robot
        self.left_wheel = 0.0
        self.right_wheel = 0.0
        self.activation = 0.0

    def loop_core(self):
        res = self.callback(self.robot)
        if len(res) == 2:
            self.left_wheel, self.right_wheel = res
            self.activation = 1.0
        else:
            self.left_wheel, self.right_wheel, self.activation = res


class BehaviorMixer(ParallelClass):
    def __init__(
            self,
            robot
    ):
        ParallelClass.__init__(self)
        self.period = 1.0 / robot.freq
        self.robot = robot
        self.behaviors = robot._behaviors
        self.condition = robot._condition
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
                activations = None
                if not self.behaviors:
                    activations = 0.0, 0.0
                else:
                    if self.mode == "random":
                        activations = self._random()
                    elif self.mode == "average":
                        activations = self._average()
                    else:
                        print(
                            self.mode,
                            'is not a valid mode. Choices are "random" or "average"',
                        )
                self.robot.left_wheel, self.robot.right_wheel = activations
                self.condition.release()
            self.robot.wait(self.period + start_time - time())

    def _average(self):
        activations = array(
            [
                (b.left_wheel, b.right_wheel, b.activation)
                for b in self.behaviors.values()
            ]
        )
        activations = average(
            activations[:, :2], weights=activations[:, 2] + 1e-10, axis=0
        )
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


class RoutineManager(object):
    def __init__(self):
        self._routines = {}

    def attach(self, routine):
        self._routines[routine.callback] = routine
        self._routines[routine.callback].start()

    def detach(self, callback):
        if callback not in self._routines:
            print(("Warning: " + callback.__name__ + " was not attached"))
        else:
            self._routines[callback].stop()  # just in case
            self._routines[callback]._terminate()
            sleep(self._routines[callback].period)
            del self._routines[callback]

    def detach_all(self):
        dict_copy = dict(self._routines)
        for callback, item in dict_copy.items():
            self.detach(callback)

    def start(self, callback):
        if callback not in self._routines:
            print(("Warning: " + callback.__name__ + " is not attached"))
            return False
        else:
            self._routines[callback].execute()
            return True

    def start_all(self):
        for callback in self._routines:
            self.start(callback)

    def stop(self, callback):
        if callback not in self._routines:
            print(("Warning: " + callback.__name__ + " is not attached"))
            return False
        else:
            self._routines[callback].stop()
            return True

    def stop_all(self):
        for callback in self._routines:
            self.stop(callback)

    def check(self, label=""):
        if not len(self._routines):
            print("No " + label.lower() + " attached")
        for callback, obj in self._routines.items():
            print(label + " \"{name}\" is attached and {started}".format(
                name=callback.__name__, started="STARTED" if obj._running.is_set() else "NOT STARTED."))
