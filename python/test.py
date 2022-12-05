import subprocess
subprocess.run("sudo tc qdisc add dev br0 root netem delay 1000ms",shell=True)