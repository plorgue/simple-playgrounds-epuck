import logging
from flask import Flask, jsonify, request

from services import SpgService
import queue, threading

main_thread_queue = queue.Queue()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

spg = SpgService()

@ app.route('/open-session', methods=['GET'])
def open_session():
    if request.method == 'GET':

        # ask main thread to start simple_playgrounds simulator
        main_thread_queue.put(lambda: spg.start_simulation())
        
        return jsonify(success=True)
        


@ app.route('/change-speed', methods=['POST'])
def change_speed():
    if request.method == 'POST':
        speed = request.form.get('speed')
        if speed == None:
            app.logger.error(f'data is not compatible. Missing arguments')
            return jsonify(success=False)

        # Modify speed of the only agent for now
        spg.set_speed(float(speed))

        app.logger.info(f'new values are : speed = {speed}')
        return jsonify(success=True)
    else:
        app.logger.info("changing speed failed")
        return jsonify(success=False)


if __name__ == "__main__":

    # launch flask in a separated thread
    threading.Thread(target=app.run).start()
    
    # main thread waits for execute process
    # especially for start the sgp simulator
    while True:
        callback = main_thread_queue.get() #blocks until an item is available
        callback()

