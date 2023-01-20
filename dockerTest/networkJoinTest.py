import docker
client = docker.from_env()
client.containers.run("ubuntu","-it",network="hugaa",name="test16",detach=False,tty=True)