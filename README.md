# User guide

## 1. Try with demo

Start server with `server/app.py`

Execute cells in `client/demo.ipynb`

## 2. The possibilities

* <b>Create agents with different characteristics</b>
    * *radius*
    * *texture*: color or spg compatible texture
    * *initial_coordinates*: ((x, y), orientation) with x, y between 0 and 1
    * *agent_type*: string usefull for behaviors
* <b>Create the playground</b>
    * *size*: (width, height)
    * *interactions*: list of interactions between agents and environnement. Only one is implemented: *BIG_EAT_SMALL* if an agent is hit by a larger one it is instantly moved to another random position.
* <b>Start (and stop) simulator with playground and agents</b>
    <br/>The *simulator_interface* supplies two functions:
    * *open_session(nb_agents, agents, playground_params)*
    <br/>This function open simple_playground with characteristics defined in *agents* and *playground_params*
    <br/>If *nb_agents* is greater than the number of *agents* then default agents will be created and return a *Simulator* instance
    * *close_session(simulator)*
    <br/>Close the simple_playground window linked to the simulator instance
* <b>Create and attach behaviors</b>
    * Agents behaviors
    Agent class has 3 functions:
        * *attach_behavior(behavior_func, freq)*
        * *start_behavior(behavior_func)*
        * *stop_behavior(behavior_func)* 
        <br/>The behavior function has one parameter the agent and must return 2 float between 0 and 1 respectively for the activation of right and left wheel
    * Sphere apparitions
    <br/>It is possible to make objects appear randomly on the field at a certain frequency. These objects can be aborbed by the agents or not.
    To do it you can use the *start_sphere_apparition* function from the simulator instance return from *open_session* with 3 parameters: *period*, *eatable* and *radius*.
    You can stop this behavior with the method *stop_sphere_apparition* 
 
## 3. Structure

<b>Server</b>

* `app.py` contains the Flask API.
* `services.py` contains the model. Manage the simulator. (used by `app.py`)
* `interactions.py` contains some function transmitted to simple_playground to managed interactions between element of the playgrounds. Currently there is only one interaction: *BIG_EAT_SMALL*. (used by `services.py`)
* `controllers/remote_controller.py` is an extensions of simple_playgrounds to control agents. (used by `services.py`)

Initialy the folders was created in anticipation of the implementation of other controllers.

<b>Client</b>
<br>Functions and class are the same or almost the same as the one used in Pyvrep-epuck

* `agents.py`contains Agent class,
* `simulator.py` contains Simulator class,
* `behaviors.py` contains Routine, Behavior, BehaviorMixer and RoutineManager class,
* `simulator_interface.py` supplies functions to start and stop simulator.
* `demo.ipynb` is an example of what it's possible to do.

## 4. Tests

A part of the server is tested with pytest (`test/test_services.py`):
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

