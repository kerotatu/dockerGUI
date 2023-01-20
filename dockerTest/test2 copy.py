import docker
client = docker.from_env()
name="hoge7"
cmd='"ubuntu", "bash",name="{}",network=na, tty=True, stdin_open=True"'.format(name)
print("aaaaaa"+cmd)
container = client.containers.create(cmd)
container.start()