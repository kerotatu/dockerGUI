#使ってない変数とかあったらミスです　消してください
#わからないことはTwitter kerotatuのDMまで 忙しかったり普通にわからなかったりするかも
from flask import Flask,request,jsonify
import json
import subprocess
import docker
import time
#Docker SDK for pythonの初期設定
client = docker.from_env()
#flaskのおまじない
app = Flask(__name__, static_folder='.', static_url_path='')
# json格納用
jsonObj=""
#遅延値格納用
delay=[]
#IPアドレス設定用
forIp=[]
#IPアドレス設定用
ipAddress=[]
#172.16.x.1のxを格納する用
Address3=[]
#172.16.1.xのxを格納する用
#基本的に変数ipAddressだけで一意に定まるが3桁目と4桁目を取り出すのが面倒なため分けている
Address4=[]

#ここで/testに行ったときにindexbが開かれる
@app.route('/test')
def index():
    return app.send_static_file('indexb.html')
#postNetworksをルーティング
@app.route('/postNetworks', methods=['POST'])
#testcon1~10を削除　1~10なのは例　ほんとうは全部削除したほうがいい
def postNetworks():
    for i in range(10):
        try:
            #基本的にdocker SDK for pythonの機能でコンテナを操作する
            container=client.containers.get("testcon"+str(i+1))
            container.stop()
            container.remove()
        except:
            pass
        
    #初期値0のリストを宣言 ここの*100はネットワークの個数　100個も作らないからもっと少なくてもいい
    ipCount=[0]*100
    #requset.get_jsonでpost送信されたjsonを受け取る
    jsonObj=request.get_json()
    obj=[]
    networkName=[]
    #jsonのままだと扱いにくいのでobjに格納していく
    for i in range(len(jsonObj)):
        obj.append(jsonObj[i])
    #送られてくるデータがcon1、con2、con1みたいになってると扱いにくいのでcon1,con1,con2にソート
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
        #ここだけはSDKを使わずにsubprocessで操作している　SDKでも良いがIPアドレスを指定できない(多分)
        #アドレスの範囲を172.16.x.0/24にしたネットワークをtestnet　x で作成するコマンド
        tmp="docker network create --driver=bridge --subnet 172.16.{}.0/24 --gateway 172.16.{}.254 testnet{}".format(24+cnt,24+cnt,e)
        cnt=cnt+1
        subprocess.run(tmp,shell=True)
    obj.pop(0)
    for e in obj:
        #コマンドの詳細については作山の資料を参照
        #testnet〇に属するコンテナをnetemtestイメージから作成するコマンド
        tmp="docker run -d -it --privileged --name testcon{} --net testnet{} --ip 172.16.{}.{} -e PASSWORD=1234  netemtest01".format(e["container"],e["bridge"],23+e["bridge"],ipCount[int(e["bridge"])]+1)
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
        # qdiscをeth0(インターフェース)に追加するコマンド
        container.exec_run("tc qdisc add dev eth0 root handle 1: htb default 5")
        print("tc qdisc add dev eth0 root handle 1: htb default 5")
        #ここの長さで何個のコンテナがネットワークに属せるかが決まる　100とかにしたいけど実行が長くなるので6でやっている。
        #１００個同じネットワークにつなげたいなら100にすること
        for i in range (6):
            # qdiscに子クラスを追加するコマンド　現状は1~6が追加される
            container.exec_run("tc class add dev eth0 parent 1: classid 1:{} htb rate 500Mbit burst 500Mbit".format(i+1))
            print("tc class add dev eth0 parent 1: classid 1:{} htb rate 500Mbit burst 500Mbit".format(i+1))
        #ipアドレスとマッチしなかった時の設定　多分使われてない　優先度を一番低くして同じネットワーク以外のすべてのipアドレスがこれを通る(通らない)　 
        container.exec_run("tc filter add dev eth0 protocol ip parent 1: prio 6 u32 match ip dst 0.0.0.0/0 flowid 1:6")
        print("tc filter add dev eth0 protocol ip parent 1: prio 6 u32 match ip dst 0.0.0.0/0 flowid 1:6")
        ip=Address4[e["container"]-1]

        for i in range(cnt+1,len(obj)):
            if(e["bridge"]==obj[i]["bridge"]):
                #遅延を追加するコマンド　
                cmd="tc qdisc add dev eth0 parent 1:{} handle {}: netem delay {}ms".format(Address4[i],10+Address4[i],int(e["value"])+int(obj[i]["value"]))
                container.exec_run(cmd)
                print(cmd)
                #その遅延を特定のIPアドレスとの通信にかけるコマンド
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
#こうしておくと他のサーバから立てても同じネットワークなら接続できる
app.run(host='0.0.0.0',port=12345, debug=True)