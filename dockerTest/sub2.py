from flask import Flask,request,jsonify
import json
import subprocess
import docker
import time
client = docker.from_env()
app = Flask(__name__, static_folder='.', static_url_path='')
jsonObj=""

forIp=[]
ipAddress=[]
Address3=[]
Address4=[]
#data=[]
#data[0]={'bridge':0,'ip':0}
@app.route('/test')
def index():
    return app.send_static_file('index.html')

@app.route('/postNetworks', methods=['POST'])
def postNetworks():
    ipCount=[0]*100
    jsonObj=request.get_json()
    obj=[]
    forIp=jsonObj
    networkName=[]
    for i in range(len(jsonObj)):
        obj.append(jsonObj[i])
    for e in obj:
        networkName.append(e["bridge"])
    networkName=set(networkName)
    cnt=0
    networkName.remove(0)
    for e in networkName:
        tmp="docker network create --driver=bridge --subnet 172.16.{}.0/24 --gateway 172.16.{}.254 netLabTestNet{}".format(24+cnt,24+cnt,e)
        #app.logger.debug(tmp)
        cnt=cnt+1
        subprocess.run(tmp,shell=True)
    obj.pop(0)
    for e in obj:
        tmp="docker run -d -it --privileged --name testcon{} --net netLabTestNet{} --ip 172.16.{}.{} -e PASSWORD=1234  netemtest01".format(e["container"],e["bridge"],23+e["bridge"],ipCount[int(e["bridge"])]+1)
        ipCount[int(e["bridge"])]+=1
        subprocess.run(tmp,shell=True)
        ipAddress.append({23+e["bridge"],ipCount[int(e["bridge"])]})
        Address3.append(23+e["bridge"])
        Address4.append(ipCount[int(e["bridge"])])

    return "aaa"

@app.route('/postLines', methods=['POST'])
def postLines():
    time.sleep(5)
    jsonObj=request.get_json()
    obj=[]
    
    for i in range(len(jsonObj)):
        obj.append(jsonObj[i])
    cnt=0
    #print("Obj")
    #print(obj)
    dlCnt=obj[0]["dl"]
    obj.pop(0)
    flagNum=[]
    for e in obj:

        container=client.containers.get("testcon"+str(e["from"]))
        if(str(e["from"]) not in flagNum):
            container.exec_run("tc qdisc add dev eth0 root handle 1: prio")
            print("tc qdisc add dev eth0 root handle 1: prio")
            #subprocess.run("tc qdisc add dev eth0 root handle 1: prio",shell=True)
            container.exec_run("tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 0.0.0.0/0 flowid 1:2")
            container.exec_run("tc filter add dev eth0 protocol ip parent 1: prio 3 u32 match ip dst 0.0.0.0/0 flowid 1:2")
            print("tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 0.0.0.0/0 flowid 1:2")
            flagNum.append(str(e["from"]))
        else:
            cmd="tc qdisc add dev eth0 parent 1:1 handle 10: netem delay {}ms".format(e["value"])
            container.exec_run(cmd)
            ip=Address4[e["from"]-1]-dlCnt
            cmd="tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 172.16.{}.{}/32 flowid 1:1".format(Address3[ip-1],ip)
            print(cmd)
            container.exec_run(cmd)

        container=client.containers.get("testcon"+str(e["to"]))
        print("testcon")
        print(str(e["to"]))
        if(str(e["to"]) not in flagNum):
            container.exec_run("tc qdisc add dev eth0 root handle 1: prio")
            print("tc qdisc add dev eth0 root handle 1: prio")
            #subprocess.run("tc qdisc add dev eth0 root handle 1: prio",shell=True)
            container.exec_run("tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 0.0.0.0/0 flowid 1:2")
            container.exec_run("tc filter add dev eth0 protocol ip parent 1: prio 3 u32 match ip dst 0.0.0.0/0 flowid 1:2")
            print("tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 0.0.0.0/0 flowid 1:2")
            flagNum.append(str(e["to"]))
        else:
            cmd="tc qdisc add dev eth0 parent 1:1 handle 10: netem delay {}ms".format(e["value"])
            container.exec_run(cmd)
            ip=Address4[e["to"]-1]-dlCnt
            cmd="tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 172.16.{}.{}/32 flowid 1:1".format(Address3[ip-1],ip)
            print(cmd)
            container.exec_run(cmd)
        
        print("flagNum")
        print(flagNum)
        #subprocess.run("tc filter add dev eth0 protocol ip parent 1: prio 2 u32 match ip dst 0.0.0.0/0 flowid 1:2",shell=True)
        #container.exec_run("tc qdisc add dev eth0 parent 1:1 handle 10: netem delay {}ms".format(e["value"]))
        cmd="tc qdisc add dev eth0 parent 1:1 handle 10: netem delay {}ms".format(e["value"])
        container.exec_run(cmd)
        print(cmd)
        #subprocess.run(cmd,shell=True)
        #print("Address4")
        #print(Address4)
        #print("e[from]")
        #print(e["from"])
        ip=Address4[e["from"]-1]-dlCnt

        #print("ip-1")
        #print(ip-1)
        #print("Address3")
        #print(Address3)
        cmd="tc filter add dev eth0 protocol ip parent 1: prio 1 u32 match ip dst 172.16.{}.{}/32 flowid 1:1".format(Address3[ip-1],ip)
        print(cmd)
        container.exec_run(cmd)
        #subprocess.run("tc filter add dev eth0 protocol ip parent 1: prio 1 u32 match ip dst 172.16.24.2/32 flowid 1:1",shell=True)
        cnt+=1
    #subprocess.run("sudo docker run -it --name test17 -h root --net nu-network --ip 172.16.24.17 -e PASSWORD=1234  ubuntu:20.04",shell=True)
    Address3.clear()
    Address4.clear()
    ipAddress.clear()
    return "aaa"
@app.route('/postTest/json')
def postTestJson():
    app.logger.debug(jsonObj)
    return "aaa"+jsonObj

app.run(port=12345, debug=True)