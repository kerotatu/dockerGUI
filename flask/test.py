from flask import Flask,request,jsonify
import json
import subprocess
app = Flask(__name__, static_folder='.', static_url_path='')
jsonObj=""
#cors = CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/test')
def index():
    return app.send_static_file('index.html')

@app.route('/postTest', methods=['POST'])
def postTest():
    jsonObj=request.get_json()
    #to=json['to']
    app.logger.debug(jsonObj)
    subprocess.run("sudo docker run -it --name test17 -h root --net nu-network --ip 172.16.24.16 -e PASSWORD=1234  ubuntu:20.04",shell=True)
    return "aaa"

@app.route('/postTest/json')
def postTestJson():
    app.logger.debug(jsonObj)
    return "aaa"+jsonObj

app.run(port=12345, debug=True)