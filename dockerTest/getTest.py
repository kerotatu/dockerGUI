import docker
import subprocess
client = docker.from_env()
name="hoge10"
#container = client.containers.create("ubuntu", "bash",name=name,network="hugaa", tty=True, stdin_open=True)
#container.start()
container=client.containers.get("hoge10")
print("a")
print((container.exec_run("ls")).output)
print("a")
subprocess.run("ls")
#subprocess.run("docker container exec -it hoge10 bash",shell=True)
#subprocess.run("pwd")