import sys, os, math

sys.path.append(os.path.join(os.getcwd(), "server"))
sys.path.append(os.path.join(os.getcwd()))

from simple_playgrounds.device.sensors import SemanticCones
import pytest
from services import SpgService
import threading, time


@pytest.mark.skip
def stop_simulator_test(spg_service):
    spg_service.start_simulation()


def test_start_stop_simulator():
    spg_service = SpgService()
    thread = threading.Thread(
        target=stop_simulator_test,
        args=(spg_service,),
    )
    thread.start()

    time.sleep(1)
    spg_service.stop_simulator()
    spg_service.reset_simulator()

    assert len(spg_service.playground.agents) == 0
    assert spg_service.done == True

def test_add_agent():
    id = 0
    initial_coordinates = ((0.5, 0.5), 2)
    type = "epuck"

    spg_service = SpgService()
    spg_service.add_agent(
        id=id, initial_coordinates=initial_coordinates, radius=12, type=type
    )

    assert len(spg_service.playground.agents) == 1
    assert spg_service.playground.agents[0].name == f"{type}_{id}"
    assert (
        spg_service.playground.agents[0].initial_coordinates[1]
        == initial_coordinates[1]
    )
    assert spg_service.playground.agents[0].initial_coordinates[0][0] == int(
        initial_coordinates[0][0] * spg_service.playground.size[0]
    )
    assert spg_service.playground.agents[0].initial_coordinates[0][1] == int(
        initial_coordinates[0][1] * spg_service.playground.size[1]
    )
    assert len(spg_service.playground.agents[0].sensors) == 2
    assert isinstance(
        spg_service.playground.agents[0].sensors[0], SemanticCones
    ) and isinstance(spg_service.playground.agents[0].sensors[1], SemanticCones)


@pytest.mark.parametrize(
    "speed,expect_speed",
    [
        ({"left": -1, "right": -1}, (-1, 0)),  # full speed backward
        ({"left": -1, "right": 1}, (0, -1)),  # spin left
        ({"left": -1, "right": 0}, (-0.5, -0.5)),  # turn left backward
        ({"left": 0, "right": 1}, (0.5, -0.5)),  # turn left forward
        ({"left": 0, "right": 0}, (0, 0)),  # stop
        ({"left": 1, "right": -1}, (0, 1)),  # spin right
        ({"left": 1, "right": 1}, (1, 0)),  # full speed forward
    ],
)
def test_set_speed(speed, expect_speed):
    spg_service = SpgService()
    spg_service.add_agent(id=0)
    name = spg_service.get_agents_names()[0]
    velocity, rotation = spg_service.set_speed(name, speed)
    assert velocity == expect_speed[0]
    assert rotation == expect_speed[1]


@pytest.mark.parametrize("id,type", [(0, None), (1, "bar")])
def test_get_agents_names(id, type):
    spg_service = SpgService()

    if type:
        spg_service.add_agent(id=id, type=type)
        assert len(spg_service.get_agents_names()) == 1
        assert spg_service.get_agents_names()[0] == f"{type}_{id}"
    else:
        spg_service.add_agent(id=id)
        assert len(spg_service.get_agents_names()) == 1
        assert spg_service.get_agents_names()[0] == f"epuck_{id}"

@pytest.mark.skip
def sensors_value_all(spg_service, main_agent, agents_detected_on_left, agents_detected_on_right, agents_not_detected):
    spg_service.start_simulation(
        agents=[
            main_agent,
            *agents_detected_on_left,
            *agents_detected_on_right,
            *agents_not_detected,
        ],
        playground={"size": (500, 500)},
    )


def test_sensors_value_all():
    RADIUS = 10
    X = Y = 200

    main_agent = {
        "id": 0,
        "initial_coordinates": ((X, Y), -math.pi / 2),
        "radius": RADIUS,
    }
    agents_not_detected = [
        {
            "id": 11,
            "initial_coordinates": ((80, Y + RADIUS + 2), 0),
            "radius": RADIUS,
        },
        {
            "id": 12,
            "initial_coordinates": ((330, Y + RADIUS + 2), 0),
            "radius": RADIUS,
        },
        {
            "id": 13,
            "initial_coordinates": ((X, 350), 0),
            "radius": RADIUS,
        },
    ]
    agents_detected_on_left = [
        {
            "id": 21,
            "initial_coordinates": ((50, Y + RADIUS), 0),
            "radius": RADIUS,
        },
        {
            "id": 22,
            "initial_coordinates": ((50, 50), 0),
            "radius": RADIUS,
        },
        {
            "id": 23,
            "initial_coordinates": ((X - RADIUS - 1, 50), 0),
            "radius": RADIUS,
        },
    ]
    agents_detected_on_right = [
        {
            "id": 31,
            "initial_coordinates": ((X + RADIUS + 1, 50), 0),
            "radius": RADIUS,
        },
        {
            "id": 32,
            "initial_coordinates": ((350, 50), 0),
            "radius": RADIUS,
        },
        {
            "id": 33,
            "initial_coordinates": ((350, Y + RADIUS), 0),
            "radius": RADIUS,
        },
    ]

    spg_service = SpgService()
    main_id = main_agent["id"]
    left_ids = [agt["id"] for agt in agents_detected_on_left]
    right_ids = [agt["id"] for agt in agents_detected_on_right]

    thread = threading.Thread(
        target=sensors_value_all,
        args=(spg_service, main_agent, agents_detected_on_left, agents_detected_on_right, agents_not_detected),
    )
    thread.start()

    time.sleep(2)

    detections = spg_service.get_agent_sensors_value(f"epuck_{main_id}", "all")

    left = [int(obj["id"]) for obj in detections["left"] if obj["is_robot"]]
    right = [int(obj["id"]) for obj in detections["right"] if obj["is_robot"]]

    assert left_ids == left
    assert right_ids == right

    spg_service.stop_simulator()


####  SKIPPED  ####


@pytest.mark.skip
def velocity_tests(spg_service, speed, expected_speed, assertions):

    time.sleep(0.5)
    spg_service.set_speed("robot_1", speed)
    spg_service.set_speed("robot_2", speed)
    time.sleep(0.5)
    spg_service.stop_simulator()

    current_speeds = spg_service.get_agents_velocity()

    assertions.append(["robot_1_in_speed", True, "robot_1" in current_speeds.keys()])
    assertions.append(["robot_2_in_speed", True, "robot_2" in current_speeds.keys()])
    assertions.append(
        ["robot_1_velocity", current_speeds["robot_1"]["velocity"], expected_speed[0]]
    )
    assertions.append(
        ["robot_2_velocity", current_speeds["robot_2"]["velocity"], expected_speed[0]]
    )
    assertions.append(
        ["robot_1_rotation", current_speeds["robot_1"]["rotation"], expected_speed[0]]
    )
    assertions.append(
        ["robot_2_rotation", current_speeds["robot_2"]["rotation"], expected_speed[0]]
    )


@pytest.mark.skip
@pytest.mark.parametrize(
    "speed,expect_speed",
    [
        ({"left": 1, "right": 1}, (1, 0)),  # full speed forward
        ({"left": -1, "right": 1}, (0, -1)),  # spin left
        ({"left": -1, "right": 0}, (-0.5, -0.5)),  # turn left backward
    ],
)
def test_get_agents_velocity(speed, expect_speed):
    spg_service = SpgService()
    assertions = []
    thread = threading.Thread(
        target=velocity_tests,
        args=(
            spg_service,
            speed,
            expect_speed,
            assertions,
        ),
    )
    thread.start()
    spg_service.start_simulation(ids=["robot_1", "robot_2"], show_image=False)
    thread.join()

    assert len(assertions) == 6
    for assertion in assertions:
        assert assertion[0] + ": " + str(assertion[1]) == assertion[0] + ": " + str(
            assertion[2]
        )
