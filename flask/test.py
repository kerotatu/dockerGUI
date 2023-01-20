from flask import Flask,request,jsonify
import json
import subprocess
import docker
client = docker.from_env()
app = Flask(__name__, static_folder='.', static_url_path='')
jsonObj=""
@app.route('/test')
def index():
    return app.send_static_file('index.html')

@app.route('/postLines', methods=['POST'])
def postLines():
    jsonObj=request.get_json()
    app.logger.debug(jsonObj)

    subprocess.run("sudo docker run -it --name test17 -h root --net nu-network --ip 172.16.24.17 -e PASSWORD=1234  ubuntu:20.04",shell=True)
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
        #tmp="docker network create --driver=bridge --subnet 172.16.{}.0/16 --gateway 1 netLabTestNet{}".format(24+cnt,e)
        subTmp="172.16.{}.0/16".format(24+cnt)
        gateTmp="172.16.{}.254".format(24+cnt)
        netName="netLabTestNet{}".format(e)
        ipam_pool = docker.types.IPAMPool(
            subnet=subTmp,
            gateway=gateTmp
        )
        ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
        )
        client.networks.create(
            netName,
            driver="bridge",
            ipam=ipam_config
        )
        #app.logger.debug(tmp)
        cnt=cnt+1
        #subprocess.run(tmp,shell=True)
    for e in obj:
        #tmp="docker run -d -it --privileged --name  --net {} --ip 172.16.24.150 -e PASSWORD=1234  ubuntu:20.04".format(e["container"])
        Cname="netLabTestCon{}".format(e["container"])
        Nname="netLabTestNet{}".format(e["network"])
        container = client.containers.create("ubuntu", "bash",name=Cname,network=Nname, tty=True, stdin_open=True)
        container.start()
        #app.logger.debug(tmp)
        #subprocess.run(tmp,shell=True)
    return "aaa"

@app.route('/postTest/json')
def postTestJson():
    app.logger.debug(jsonObj)
    return "aaa"+jsonObj

app.run(port=12345, debug=True)