import docker
from vm_manager.docker_utils.docker_client import get_docker_client

class NetworkManager:
    def __init__(self):
        self.client = get_docker_client()

    # creeaza o retea noua daca nu exista deja
    def create_network(self, network_name, subnet=None):
        try:
            self.client.networks.get(network_name)
            return False
        except docker.errors.NotFound:
            ipam_config = None
            if subnet:
                ipam_pool = docker.types.IPAMPool(
                    subnet=subnet
                )
                ipam_config = docker.types.IPAMConfig(
                    pool_configs=[ipam_pool]
                )
            
            self.client.networks.create(
                network_name, 
                driver="bridge",
                ipam=ipam_config
            )
            return True

    # sterge o retea existenta
    def delete_network(self, network_name):
        try:
            network = self.client.networks.get(network_name)
            network.remove()
            return True, f"Network {network_name} deleted."
        except Exception as e:
            return False, str(e)

    # listeaza toate retelele disponibile
    def list_networks(self):
        try:
            networks = self.client.networks.list(filters={"driver": "bridge"})
            return [n.name for n in networks if n.name != "bridge"]
        except Exception:
            return []

    # conecteaza o masina virtuala la o retea
    def connect_vm(self, vm_name, network_name):
        try:
            network = self.client.networks.get(network_name)
            network.connect(vm_name)
            return True
        except Exception as e:
            return str(e)

    # deconecteaza o masina virtuala de la o retea
    def disconnect_vm(self, vm_name, network_name):
        try:
            network = self.client.networks.get(network_name)
            network.disconnect(vm_name)
            return True
        except Exception as e:
            return str(e)

