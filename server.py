from flask import Flask, jsonify, request


from data_explorer.app import DataExplorer


def create_app():
    """Create app-server to trigger application from an api."""
    # app initiliazation
    app = Flask(__name__)

    # initialize app
    data_explorer = DataExplorer()

    @app.route('/')
    def explore(pump_type):
        timeseries = request.args.get('timeseries', type=str)
        start = request.args.get('start', None, type=int)
        end = request.args.get('end', None, type=int)

        data = data_explorer.explore(
            timeseries=timeseries,
            start=start,
            end=end,
        )
        response = {
            'data': data,
            'status': 'ok'
        }
        return jsonify(response)

    return app
