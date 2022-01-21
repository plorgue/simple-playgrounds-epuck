from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simple_playgrounds.playground.playground import Playground
from simple_playgrounds.playground.collision_handlers import get_colliding_entities
from simple_playgrounds.agent.agent import Agent

import math
from random import random


def big_ones_eat_small_ones(arbiter, space, data):
    playground: Playground = data["playground"]
    (_, agent1), (_, agent2) = get_colliding_entities(playground, arbiter)

    assert isinstance(agent1, Agent)
    assert isinstance(agent2, Agent)

    if agent1.base_platform.radius > agent2.base_platform.radius:
        agent2.position, agent2.angle = (
            (
                int(playground.size[0] * random()),
                int(playground.size[1] * random()),
            ),
            2 * math.pi * random(),
        )
        agent2.velocity = (0, 0)
        return True
    elif agent1.base_platform.radius < agent2.base_platform.radius:
        agent1.position, agent1.angle = (
            (
                int(playground.size[0] * random()),
                int(playground.size[1] * random()),
            ),
            2 * math.pi * random(),
        )
        agent1.velocity = (0, 0)
        return True
    else:
        return False