import sys, os

sys.path.append(os.path.join(os.getcwd(), "server"))
sys.path.append(os.path.join(os.getcwd()))

import pytest
from simple_playgrounds.agents.sensors import Proximity
from services import SpgService
import threading, time, queue


@pytest.mark.parametrize(
    "nb_agent,ids, sensor", 
    [
        (1, [], None),
        (3, [], None),
        (3, [], 'proximiter'),
        (0, ['foo', 'bar'], None),
        (3, ['foo', 'bar'], 'proximiter'),
    ])
def test_add_agent(nb_agent, ids, sensor):
    spg_service = SpgService()
    spg_service.add_agents(nb_agent=nb_agent, sensor=sensor, ids=ids)
    real_nb_of_agent = nb_agent
    
    if len(ids) > 0:
        real_nb_of_agent = len(ids) 
    assert len(spg_service.playground.agents) == real_nb_of_agent
    
    for agent in spg_service.playground.agents:
        if len(ids) > 0:
            assert agent.name in ids
            ids.pop(ids.index(agent.name))
        for sensor in agent.sensors:
            assert type(sensor) == Proximity

@pytest.mark.parametrize(
    "speed,expect_speed", 
    [
        ({"left": -1, "right": -1}, (-1, 0)),     # full speed backward
        ({"left": -1, "right": 1}, (0, -1)),      # spin left
        ({"left": -1, "right": 0}, (-0.5, -0.5)), # turn left backward 
        ({"left": 0, "right": 1}, (0.5, -0.5)),   # turn left forward
        ({"left": 0, "right": 0}, (0, 0)),        # stop
        ({"left": 1, "right": -1}, (0, 1)),       # spin right
        ({"left": 1, "right": 1}, (1, 0)),        # full speed forward
    ])
def test_set_speed(speed, expect_speed):
    spg_service = SpgService()
    spg_service.add_agents(nb_agent=1, sensor=None)
    name = spg_service.get_agents_names()[0]
    velocity, rotation = spg_service.set_speed(name, speed)
    assert velocity == expect_speed[0]
    assert rotation == expect_speed[1]

def test_get_agents_names():
    spg_service = SpgService()
    nb_agent = 1
    spg_service.add_agents(nb_agent=nb_agent, sensor=None)
    assert len(spg_service.get_agents_names()) == nb_agent

@pytest.mark.skip
def velocity_tests(spg_service, speed, expected_speed, assertions):

    time.sleep(0.5)
    spg_service.set_speed('robot_1', speed)
    spg_service.set_speed('robot_2', speed)
    time.sleep(0.5)
    spg_service.stop_simulator()

    current_speeds = spg_service.get_agents_velocity()

    assertions.append(['robot_1_in_speed', True ,'robot_1' in current_speeds.keys()])
    assertions.append(['robot_2_in_speed', True ,'robot_2' in current_speeds.keys()])
    assertions.append(['robot_1_velocity', current_speeds['robot_1']['velocity'], expected_speed[0]])
    assertions.append(['robot_2_velocity', current_speeds['robot_2']['velocity'], expected_speed[0]])
    assertions.append(['robot_1_rotation', current_speeds['robot_1']['rotation'], expected_speed[0]])
    assertions.append(['robot_2_rotation', current_speeds['robot_2']['rotation'], expected_speed[0]])


@pytest.mark.parametrize(
    "speed,expect_speed", 
    [
        ({"left": 1, "right": 1}, (1, 0)),        # full speed forward
        ({"left": -1, "right": 1}, (0, -1)),      # spin left
        ({"left": -1, "right": 0}, (-0.5, -0.5)), # turn left backward 
    ])
def test_get_agents_velocity(speed, expect_speed):
    spg_service = SpgService()
    assertions = []
    thread = threading.Thread(target=velocity_tests, args=(spg_service, speed, expect_speed, assertions,))
    thread.start()
    spg_service.start_simulation(ids=['robot_1', 'robot_2'])
    thread.join()

    assert len(assertions) == 6
    for assertion in assertions:
        assert assertion[0]+': '+str(assertion[1]) == assertion[0]+': '+str(assertion[2])

@pytest.mark.skip
def stop_simulator_test(spg_service, assertions):
    time.sleep(0.5)
    spg_service.stop_simulator()
    assertions.append(['nb_agent',len(spg_service.engine.playground.agents), 0])

def test_start_stop_simulator():
    spg_service = SpgService()
    assertions = []
    thread = threading.Thread(target=stop_simulator_test, args=(spg_service,assertions,))
    thread.start()
    spg_service.start_simulation()
    thread.join()

    assert len(assertions) == 1
    for assertion in assertions:
        assert assertion[0]+': '+str(assertion[1]) == assertion[0]+': '+str(assertion[2])

