from vm_manager.core.virtual_machine import VirtualMachine
from vm_manager.core.network_manager import NetworkManager
from vm_manager.config.settings import VM_IMAGE, CONTAINER_PREFIX
from vm_manager.docker_utils.docker_client import get_docker_client
import docker

class ResourceManager:
    def __init__(self):
        self.vms = {}
        self.network_manager = NetworkManager()
        self.client = get_docker_client()
        self._load_existing_vms()

    # incarca masinile virtuale existente la pornire
    def _load_existing_vms(self):
        try:
            containers = self.client.containers.list(all=True)
            for container in containers:
                if container.name.startswith(CONTAINER_PREFIX):
                    vm = VirtualMachine(container.name, VM_IMAGE)
                    self.vms[container.name] = vm
        except Exception as e:
            print(f"Error loading existing VMs: {e}")

    # creeaza o noua masina virtuala
    def create_vm(self, name):
        full_name = f"{CONTAINER_PREFIX}{name}"
        if full_name in self.vms:
            raise ValueError(f"VM {name} already exists.")
        
        vm = VirtualMachine(full_name, VM_IMAGE)
        vm.start()
        self.vms[full_name] = vm
        return vm

    # sterge o masina virtuala
    def delete_vm(self, name):
        full_name = f"{CONTAINER_PREFIX}{name}" if not name.startswith(CONTAINER_PREFIX) else name
        if full_name in self.vms:
            vm = self.vms[full_name]
            vm.remove()
            del self.vms[full_name]

    # porneste o masina virtuala
    def start_vm(self, name):
        full_name = f"{CONTAINER_PREFIX}{name}" if not name.startswith(CONTAINER_PREFIX) else name
        if full_name in self.vms:
            self.vms[full_name].start()

    # opreste o masina virtuala
    def stop_vm(self, name):
        full_name = f"{CONTAINER_PREFIX}{name}" if not name.startswith(CONTAINER_PREFIX) else name
        if full_name in self.vms:
            self.vms[full_name].stop()

    # returneaza lista cu toate masinile virtuale
    def get_all_vms(self):
        for vm in self.vms.values():
            vm.refresh_status()
        return list(self.vms.values())

    # returneaza retelele disponibile
    def get_available_networks(self):
        return self.network_manager.list_networks()

    # creeaza o retea prin network manager
    def create_network(self, network_name, subnet=None):
        return self.network_manager.create_network(network_name, subnet)

    # sterge o retea
    def delete_network(self, network_name):
        return self.network_manager.delete_network(network_name)

    # conecteaza vm la retea
    def connect_vm_to_network(self, vm_name, network_name):
        full_name = f"{CONTAINER_PREFIX}{vm_name}" if not vm_name.startswith(CONTAINER_PREFIX) else vm_name
        return self.network_manager.connect_vm(full_name, network_name)

    # deconecteaza vm de la retea
    def disconnect_vm_from_network(self, vm_name, network_name):
        full_name = f"{CONTAINER_PREFIX}{vm_name}" if not vm_name.startswith(CONTAINER_PREFIX) else vm_name
        return self.network_manager.disconnect_vm(full_name, network_name)

    # ruleaza o comanda pe vm
    def run_command_on_vm(self, name, cmd, stream=False):
        full_name = f"{CONTAINER_PREFIX}{name}" if not name.startswith(CONTAINER_PREFIX) else name
        if full_name in self.vms:
            return self.vms[full_name].run_command(cmd, stream=stream)
        return "VM not found"

    # actualizeaza resursele (cpu/ram) pentru vm
    def update_vm_resources(self, name, cpu, ram):
        full_name = f"{CONTAINER_PREFIX}{name}" if not name.startswith(CONTAINER_PREFIX) else name
        if full_name in self.vms:
            return self.vms[full_name].update_resources(cpu, ram)
        return False, "VM not found"

    # urca un fisier pe vm
    def upload_file_to_vm(self, name, src, dest):
        full_name = f"{CONTAINER_PREFIX}{name}" if not name.startswith(CONTAINER_PREFIX) else name
        if full_name in self.vms:
            return self.vms[full_name].upload_file(src, dest)
        return False, "VM not found"
