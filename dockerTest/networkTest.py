import docker
client = docker.from_env()
ipam_pool = docker.types.IPAMPool(
    subnet='192.168.53.0/24',
    gateway='192.168.53.254'
)
ipam_config = docker.types.IPAMConfig(
    pool_configs=[ipam_pool]
)
client.networks.create(
    "hugaa2",
    driver="bridge",
    ipam=ipam_config
)