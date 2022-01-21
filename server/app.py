import logging
import queue
import threading

import numpy as np
from flask import Flask, jsonify, request, Response

from services import SpgService

main_thread_queue = queue.Queue()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

spg = SpgService()


@app.route("/simulator/open", methods=["GET"])
def open_session():
    data = request.get_json().get('json')

    # ask main thread to start simple_playgrounds simulator
    main_thread_queue.put(lambda: spg.start_simulation(**data))
    return Response(status=200)


@app.route("/agent/change-speed", methods=["POST"])
def change_speed():
    if request.method == "POST":
        data = request.get_json().get('json')
        agent_id = data["agent_id"]
        speeds = data["new_speeds"]
        if speeds is None or agent_id is None:
            app.logger.error(f"data is not compatible. Missing arguments")
            return jsonify(success=False)

        # Modify the speeds of the agent
        velocity, rotation = spg.set_speed(
            agent_id,
            {
                "left": speeds[0],
                "right": speeds[1]
            }
        )
        app.logger.info(f"new values are : speed = {velocity}, rotation = {rotation}")
        return jsonify(success=True)
    else:
        app.logger.info("changing speed failed")
        return jsonify(success=False)


@app.route("/simulator/close", methods=["POST"])
def stop_simulator():
    if request.method == "POST":
        if spg.state_simulator == spg.STATE_RUNNING:
            spg.stop_simulator()
            spg.reset_simulator()
            return jsonify(success=True)
    return jsonify(success=False)


@app.route("/simulator/reset", methods=["POST"])
def reset_simulator():
    if request.method == "POST":
        if spg.state_simulator == spg.STATE_WAITING:
            spg.reset_simulator()
            return jsonify(success=True)
    return jsonify(success=False)


@app.route("/agents")
def agents():
    if request.method == "GET":
        return jsonify({"data": {"names": spg.get_agents_names()}})


@app.route("/agent/prox-activations")
def agent_sensor_value():
    if request.method == "GET":
        
        data = request.get_json().get('json')
        agent_name = None
        if type(data) is dict:
            agent_name = data.get('agent_name')

        if spg.state_simulator == spg.STATE_STOPPED:
            return Response(status=500)
        elif agent_name:
            try:
                detect = spg.get_agent_sensors_value(agent_name)
                return jsonify(detect)
            except ValueError as e:
                return Response(str(e), status=404)
        else:
            return Response(status=400)


@app.route("/simulator")
def simulator_status():
    if request.method == "GET":
        return jsonify({"data": {"status": spg.state_simulator}})


@app.route("/simulator/add-sphere", methods=["POST"])
def add_sphere():
    if request.method == "POST":
        data = request.get_json().get('json')
        name = data["name"]
        position = data["position"]
        sizes = data["sizes"]
        mass = data["mass"]
        eatable = data["eatable"]
        spg.add_sphere(
            name,
            np.array(position) * np.array(spg.playground.size),
            np.array(sizes) * np.array(spg.playground.size),
            mass,
            eatable
        )
        return jsonify(success=True)
    return jsonify(success=False)


# @app.route("/agents/speed")
# def agents_speed():
#     if request.method == "GET":
#         return jsonify({"data": spg.get_agents_velocity()})


# @app.route("/agents/position")
# def agents_position():
#     if request.method == "GET":
#         return jsonify({"data": spg.get_agents_position()})


# @app.route("/agent/<name>")
# def an_agent(name):
#     if request.method == "GET":

#         return jsonify(
#             {
#                 "data": {
#                     "name": name,
#                     "position": spg.get_agents_position()[name],
#                     "velocity": spg.get_agents_velocity()[name]["velocity"],
#                     "rotation": spg.get_agents_velocity()[name]["rotation"],
#                     "sensors": spg.get_agent_sensors(name)["sensors"],
#                 }
#             }
#         )


# @app.route("/agent/<name>/sensor/<sensor>")
# def a_sensor(name, sensor):
#     if request.method == "GET":

#         return jsonify({"data": spg.get_agent_sensor_value(name, sensor)})


if __name__ == "__main__":

    # launch flask in a separated thread
    threading.Thread(target=app.run).start()

    # main thread waits for execute process
    # especially for start the sgp simulator
    while True:
        callback = main_thread_queue.get()  # blocks until an item is available
        callback()
