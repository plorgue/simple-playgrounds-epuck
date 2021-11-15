from logging import ERROR
import logging
from flask import Flask, jsonify, request

from spg_mock import SpgMock
import queue, threading

callback_queue = queue.Queue()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

mock = SpgMock()

@ app.route('/open-session', methods=['GET'])
def open_session():
    if request.method == 'GET':

        #
        callback_queue.put(lambda: mock.start_simulation())
        
        return jsonify(success=True)
        


@ app.route('/change-speed', methods=['POST'])
def change_speed():
    if request.method == 'POST':
        speed = request.form.get('speed')
        if speed == None:
            app.logger.error(f'data is not compatible. Missing arguments')
            return jsonify(success=False)

        # Here the new values should be assigned to the agent (maybe using asyncIO ?)
        mock.set_speed(float(speed))

        app.logger.info(f'new values are : speed = {speed}')
        return jsonify(success=True)
    else:
        app.logger.info("changing speed failed")
        return jsonify(success=False)


if __name__ == "__main__":

    #
    threading.Thread(target=app.run).start()
    
    #
    while True:
        callback = callback_queue.get() #blocks until an item is available
        callback()

