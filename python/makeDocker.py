import subprocess
subprocess.run("sudo docker run -it --name test16 -h root --net nu-network --ip 172.16.24.16 -e PASSWORD=1234  ubuntu:20.04",shell=True)