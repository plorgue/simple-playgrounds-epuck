from flask import Flask, jsonify, request
from werkzeug.wrappers import response

from spg_mock import SpgMock

app = Flask(__name__)
mock = SpgMock()

@ app.route('/open-session', methods=['GET'])
def open_session():
    if request.method == 'GET':
        pg, agent = mock.start_simulation()
        if pg != None and agent != None:
            app.logger.info("Simulation start")
            return jsonify(success=True)
        else:
            app.logger.info("Impossible to start simulation")
            return jsonify(success=False)


@ app.route('/change-speed', methods=['POST'])
def change_speed():
    print("here")
    if request.method == 'POST':
        speed_left = request.form.get('speed_left')
        speed_right = request.form.get('speed_right')
        epuck = request.form.get('epuck')
        if speed_left == None or speed_right == None or epuck == None:
            app.logger.error(
                f'data is not compatible. Missing arguments')
            return jsonify(success=False)
        
        # Here the new values should be assigned to the agent (maybe using asyncIO ?)
        mock.set_speed(speed_left)

        app.logger.info(
            f'new values are : speed_left = {speed_left} and speed_right = {speed_right}')
        return jsonify(success=True)
    else:
        app.logger.info("changing speed failed")
        return jsonify(success=False)


if __name__ == "__main__":
    app.run(debug=True)
