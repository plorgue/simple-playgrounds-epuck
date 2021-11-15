from flask import Flask, jsonify, request
from werkzeug.wrappers import response

from spg_mock import SpgMock
import queue, threading

#somewhere accessible to both:
callback_queue = queue.Queue()


app = Flask(__name__)
mock = SpgMock()

@ app.route('/open-session', methods=['GET'])
def open_session():
    if request.method == 'GET':
        callback_queue.put(lambda: mock.start_simulation())
        # return simulator and agents ids
        return jsonify(success=True)
        


@ app.route('/change-speed', methods=['POST'])
def change_speed():
    if request.method == 'POST':
        speed_left = request.form.get('speed_left')
        speed_right = request.form.get('speed_right')
        epuck = request.form.get('epuck')
        if speed_left == None or speed_right == None or epuck == None:
            app.logger.error(
                f'data is not compatible. Missing arguments')
            return jsonify(success=False)
        
        # Here the new values should be assigned to the agent (maybe using asyncIO ?)
        mock.set_speed(float(speed_left))

        app.logger.info(
            f'new values are : speed_left = {speed_left} and speed_right = {speed_right}')
        return jsonify(success=True)
    else:
        app.logger.info("changing speed failed")
        return jsonify(success=False)
    

if __name__ == "__main__":
    threading.Thread(target=app.run).start()
    while True:
        callback = callback_queue.get() #blocks until an item is available
        callback()

