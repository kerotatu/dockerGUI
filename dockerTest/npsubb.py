from flask import Flask,request,jsonify
import json
import subprocess
import docker
import time
client = docker.from_env()
app = Flask(__name__, static_folder='.', static_url_path='')
jsonObj=""
delay=[]
forIp=[]
ipAddress=[]
Address3=[]
Address4=[]

@app.route('/test')
def index():
    return app.send_static_file('indexb.html')

@app.route('/postNetworks', methods=['POST'])
def postNetworks():
    for i in range(10):
        try:
            container=client.containers.get("testcon"+str(i+1))
            container.stop()
            container.remove()
        except:
            pass
        

    ipCount=[0]*100
    jsonObj=request.get_json()
    obj=[]
    forIp=jsonObj
    networkName=[]
    for i in range(len(jsonObj)):
        obj.append(jsonObj[i])
    obj.sort(key=lambda x: x["container"])
    print(obj)
    for e in obj:
        networkName.append(e["bridge"])
        delay.append(e["value"])
    networkName=set(networkName)
    cnt=0
    print("objtype===================")
    print(type(obj))
    delay.remove(0)
    networkName.remove(0)
    for e in networkName:
        tmp="docker network create --driver=bridge --subnet 172.16.{}.0/24 --gateway 172.16.{}.254 netLabTestNet{}".format(24+cnt,24+cnt,e)
        cnt=cnt+1
        subprocess.run(tmp,shell=True)
    obj.pop(0)
    for e in obj:
        tmp="docker run -d -it --privileged --name testcon{} --net netLabTestNet{} --ip 172.16.{}.{} -e PASSWORD=1234  ubuntu:20.04".format(e["container"],e["bridge"],23+e["bridge"],ipCount[int(e["bridge"])]+1)
        ipCount[int(e["bridge"])]+=1
        subprocess.run(tmp,shell=True)
        
        ipAddress.append({23+e["bridge"],ipCount[int(e["bridge"])]})
        Address3.append(23+e["bridge"])
        Address4.append(ipCount[int(e["bridge"])])
    print("obj=")
    print(obj)

    time.sleep(5)
    cnt=0

    for e in obj:
        container=client.containers.get("testcon"+str(e["container"]))

        print("testcon")
        print(str(e["container"]))
        container.exec_run("tc qdisc add dev eth0 root handle 1: htb default 5")
        print("tc qdisc add dev eth0 root handle 1: htb default 5")
        for i in range (6):
            container.exec_run("tc class add dev eth0 parent 1: classid 1:{} htb rate 500Mbit burst 500Mbit".format(i+1))
            print("tc class add dev eth0 parent 1: classid 1:{} htb rate 500Mbit burst 500Mbit".format(i+1))
        container.exec_run("tc filter add dev eth0 protocol ip parent 1: prio 6 u32 match ip dst 0.0.0.0/0 flowid 1:6")
        print("tc filter add dev eth0 protocol ip parent 1: prio 6 u32 match ip dst 0.0.0.0/0 flowid 1:6")
        ip=Address4[e["container"]-1]

        for i in range(cnt+1,len(obj)):
            if(e["bridge"]==obj[i]["bridge"]):
                cmd="tc qdisc add dev eth0 parent 1:{} handle {}: netem delay {}ms".format(ip,10+ip,int(e["value"])+int(obj[i]["value"]))
                container.exec_run(cmd)
                print(cmd)
                cmd="tc filter add dev eth0 protocol ip parent 1: prio {} u32 match ip dst 172.16.{}.{}/32 flowid 1:{}".format(ip,23+e["bridge"],Address4[i],Address4[i])
                print(cmd)
                container.exec_run(cmd)
        cnt+=1
    Address3.clear()
    Address4.clear()
    ipAddress.clear()
    return "aaa"

@app.route('/postLines', methods=['POST'])
def postLines():
    
    return "aaa"
@app.route('/postTest/json')
def postTestJson():
    app.logger.debug(jsonObj)
    return "aaa"+jsonObj

app.run(port=12345, debug=True)