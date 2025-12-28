import docker

# ne conectam la docker
def get_docker_client():
    return docker.from_env()
