# User guide

## 1. Try with demo

Start server with `server/app.py`

Execute cells in `client/demo.ipynb`

## 2. The possibilities

* Create agents with different characteristics:
    * *radius*
    * *texture*: color or spg compatible texture
    * *initial_coordinates*: ((x, y), orientation) with x, y between 0 and 1
    * *agent_type*: string usefull for behaviors
* Create the playground:
    * *size*: (width, height)
    * *interactions*: list of interactions between agents and environnement. Only one is implemented: *BIG_EAT_SMALL* if an agent is hit by a larger one it is instantly moved to another random position.
* Start simulator with playground and agents
    * open_session(nb_agents, agents, playground_params)
* Create and attach behaviors
    * Agents behaviors
    ..
    * Sphere apparitions
    ..
* Stop behaviors
..
* Close simulator
..
 
## 3. Tests

A part of the server is tested with pytest:
* start / stop simulator
* add agents
* change speed agents
* attach and retrieve agents type
* consistent sensor values according agents positions

# Installation

Library and dependencies via [poetry](https://python-poetry.org/docs/)
```bash
poetry install
```

