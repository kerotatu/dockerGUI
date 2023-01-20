from flask import Flask,request,jsonify
import json
import subprocess
import docker
client = docker.from_env()
app = Flask(__name__, static_folder='.', static_url_path='')
jsonObj=""
ipCount=[0]*100
@app.route('/test')
def index():
    return app.send_static_file('index.html')

@app.route('/postLines', methods=['POST'])
def postLines():
    jsonObj=request.get_json()
    obj=[]
    for i in range(len(jsonObj)):
        app.logger.debug(i)
        obj.append(jsonObj[i])
        app.logger.debug(obj[i])
     
    app.logger.debug(jsonObj)
    for i in range(len(jsonObj)):
        #app.logger.debug(i)
        obj.append(jsonObj[i])
        #app.logger.debug(obj[i])

    for e in obj:
        container=client.containers.get("netLabTestCon"+e["to"])
        container.exec_run("tc qdisc add dev eth0 root handle 1: prio")
        #subprocess.run("tc qdisc add dev eth0 root handle 1: prio",shell=True)
        container.exec_run("tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 0.0.0.0/0 flowid 1:2")
        #subprocess.run("tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 0.0.0.0/0 flowid 1:2",shell=True)
        container.exec_run("tc qdisc add dev eth0 parent 1:1 handle 10: netem delay {}ms".format(e["value"]))
        #cmd="tc qdisc add dev eth0 parent 1:1 handle 10: netem delay {}ms".format()
        #subprocess.run(cmd,shell=True)
        ip=e["to"]
        for i in range(int(e["network"])-1):
            ip=ip-ipCount[i]
        container.exec_run("tc filter add dev eth0 protocol ip parent 1: prio 1 u32 match ip dst 172.16.{}.{}/32 flowid 1:1".format(24+e["network"],ip))
        #subprocess.run("tc filter add dev eth0 protocol ip parent 1: prio 1 u32 match ip dst 172.16.24.2/32 flowid 1:1",shell=True)
    #subprocess.run("sudo docker run -it --name test17 -h root --net nu-network --ip 172.16.24.17 -e PASSWORD=1234  ubuntu:20.04",shell=True)
    return "aaa"

@app.route('/postNetworks', methods=['POST'])
def postNetworks():
    jsonObj=request.get_json()
    obj=[]
    networkName=[]
    app.logger.debug(jsonObj[0])
    for i in range(len(jsonObj)):
        app.logger.debug(i)
        obj.append(jsonObj[i])
        app.logger.debug(obj[i])
    
    app.logger.debug(obj[1]["bridge"])
    for e in obj:
        networkName.append(e["bridge"])
    
    networkName=set(networkName)
    app.logger.debug(networkName)
    cnt=0
    for e in networkName:
        tmp="docker network create --driver=bridge --subnet 172.16.{}.0/16 --gateway 1 netLabTestNet{}".format(24+cnt,e)
        #app.logger.debug(tmp)
        cnt=cnt+1
        subprocess.run(tmp,shell=True)

    
    for e in obj:
        tmp="docker run -d -it --privileged --name  --net netLabTestCon{} --ip 172.16.{}.{} -e PASSWORD=1234  ubuntu:20.04".format(e["container"],24+e["network"],ipCount[int(e["netWork"])]+1)
        ipCount[int(e["netWork"])]+=1
        #app.logger.debug(tmp)
        subprocess.run(tmp,shell=True)
    return "aaa"

@app.route('/postTest/json')
def postTestJson():
    app.logger.debug(jsonObj)
    return "aaa"+jsonObj

app.run(port=12345, debug=True)