from flask import Flask, request, jsonify
from flask_cors import CORS
import signal
import json
from werkzeug.serving import make_server
import traceback
import logging

logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p',
                        filename='speech_system.log',
                        filemode='w',
                        level=logging.DEBUG)

from pipeline_orchestrator import PipelineOrchestrator
from explainability.explain_responses import ExplainResponses

app = Flask(__name__)
CORS(app)

PO = None  # Global object for the pipeline orchestrator
is_shutting_down = False

def init():
    print("Initialization started")
    global PO
    PO = PipelineOrchestrator()
    
@app.route('/')
def index():                                    # Just used to ping server, and see if its online
    return 'Online'        

@app.route("/api/sendMessage", methods=['POST'])
def sendMessage():
    exp_response = ExplainResponses()
    global PO
    data = request.get_json()
    message = PO.send_response(data['message'])
    explanation = exp_response.overall_explanation()
    exp_response.clear_explanation()
    response = jsonify({'message': message,'explanation': explanation})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/api/getDepTree", methods=['POST'])
def getDependencyTree():
    global PO
    data = request.get_json()
    svg = PO.get_dependency_tree(data['message'])
    response = jsonify({'svg': svg})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def shutdown_stop(signum, frame):
    global PO
    global is_shutting_down
    if not is_shutting_down:
        is_shutting_down = True
        print('Received termination signal. Shutting down gracefully...')
        # perform cleanup    
        PO.stop()
        exit(1)
    
signal.signal(signal.SIGINT, shutdown_stop)
signal.signal(signal.SIGTERM, shutdown_stop)

if __name__ == "__main__":
    try:
        init()
        print("Initialization success")
    except Exception as e:
        traceback.print_exc()
        print("Error in Initialization: ", e)
        exit(1)
    app.run(debug=True,host='0.0.0.0', port=5000, use_reloader=False)  # run our Flask app