import docker
client = docker.from_env()

container = client.containers.run("iris-model:latest", detach=True)

for line in container.logs(stream=True):
    print(line.decode('utf-8').strip())
