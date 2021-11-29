import logging
from flask import Flask, jsonify, request
import requests

from services import SpgService
import queue, threading

main_thread_queue = queue.Queue()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

spg = SpgService()

@ app.route('/open-session', methods=['GET'])
def open_session():
    if request.method == 'GET':
        nb_agent = request.json.get('nb_agent')
        print(nb_agent)
        # ask main thread to start simple_playgrounds simulator
        main_thread_queue.put(lambda: spg.start_simulation(nb_agent))
        
        return jsonify(success=True)

@ app.route('/change-speed', methods=['POST'])
def change_speed():
    if request.method == 'POST':
        speed = request.json.get('speed')
        agent_name = request.json.get('name')
        if speed == None or agent_name == None:
            app.logger.error(f'data is not compatible. Missing arguments')
            return jsonify(success=False)

        # Modify speed of the only agent for now
        velocity, rotation = spg.set_speed(agent_name, speed)

        app.logger.info(f'new values are : speed = {velocity}, rotation = {rotation}')
        return jsonify(success=True)
    else:
        app.logger.info("changing speed failed")
        return jsonify(success=False)

@ app.route('/agents')
def agents():
    if request.method == 'GET':
        return jsonify({'data': {'names': spg.get_agents_names()}})

@ app.route('/agents/speed')
def agents_speed():
    if request.method == 'GET':
        return jsonify({'data': spg.get_agents_velocity()})

@ app.route('/agents/position')
def agents_position():
    if request.method == 'GET':
        return jsonify({'data': spg.get_agents_position()})


if __name__ == "__main__":

    # launch flask in a separated thread
    threading.Thread(target=app.run).start()
    
    # main thread waits for execute process
    # especially for start the sgp simulator
    while True:
        callback = main_thread_queue.get() #blocks until an item is available
        callback()

