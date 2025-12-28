import docker
import tarfile
import io
import os
from vm_manager.docker_utils.docker_client import get_docker_client
from vm_manager.config.settings import DEFAULT_CPU, DEFAULT_RAM

class VirtualMachine:
    # initializam masina virtuala cu setarile default
    def __init__(self, name, image):
        self.name = name
        self.image = image
        self.client = get_docker_client()
        self.container = None
        self.state = "stopped"
        self.ip_address = "N/A"
        self.networks = {}
        # urmarim resursele alocate
        self.cpu_limit = DEFAULT_CPU
        self.ram_limit = DEFAULT_RAM
        self.workdir = "/" # directorul de lucru implicit
        
        self.refresh_status()

    # actualizam starea si ip-ul masinii virtuale
    def refresh_status(self):
        try:
            self.container = self.client.containers.get(self.name)
            self.state = self.container.status
            
            if self.state == "running":
                pass

            # obtinem adresele ip din toate retelele
            self.networks = {}
            if self.container.attrs['NetworkSettings']['Networks']:
                net_settings = self.container.attrs['NetworkSettings']['Networks']
                for net_name, net_data in net_settings.items():
                    self.networks[net_name] = net_data['IPAddress']
                
                # formatam pentru afisare
                self.ip_address = "\n".join([f"{n}: {ip}" for n, ip in self.networks.items()])
            else:
                self.ip_address = "No Network"
                
        except docker.errors.NotFound:
            self.container = None
            self.state = "stopped"
            self.ip_address = "N/A"
            self.networks = {}
        except Exception as e:
            print(f"Error refreshing status for {self.name}: {e}")

    # pornim containerul docker
    def start(self):
        if self.container:
            if self.state == "exited" or self.state == "stopped":
                self.container.start()
                self.refresh_status()
        else:
            # cream si pornim containerul
            try:
                nano_cpus = int(self.cpu_limit * 1_000_000_000)
                self.container = self.client.containers.run(
                    self.image,
                    name=self.name,
                    detach=True,
                    network="bridge", # folosim reteaua implicita bridge
                    command="tail -f /dev/null", # mentinem containerul activ
                    hostname=self.name,
                    dns=['8.8.8.8', '8.8.4.4'], # asiguram functionarea dns
                    # limite resurse
                    nano_cpus=nano_cpus,
                    mem_limit=self.ram_limit
                )
                self.refresh_status()
            except Exception as e:
                print(f"Failed to start VM {self.name}: {e}")

    # modificam limitele de cpu si ram
    def update_resources(self, cpu, ram):
        self.cpu_limit = float(cpu)
        self.ram_limit = ram
        
        if self.container:
            try:
                nano_cpus = int(self.cpu_limit * 1_000_000_000)
                self.container.update(
                    nano_cpus=nano_cpus,
                    mem_limit=self.ram_limit
                )
                return True, f"Updated: {cpu} CPU, {ram} RAM"
            except Exception as e:
                return False, str(e)
        return True, "Settings saved (will apply on create)"

    # urcam fisiere in container folosind arhiva tar
    def upload_file(self, src_path, dest_path):
        if not self.container or self.state != "running":
            return False, "VM is not running"
        
        try:
            # cream arhiva tar in memorie
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode='w') as tar:
                # adaugam fisierul in arhiva
                tar.add(src_path, arcname=os.path.basename(src_path))
            
            stream.seek(0)
            
            # punem arhiva in container
            self.container.put_archive(
                path=dest_path,
                data=stream
            )
            return True, f"Uploaded {os.path.basename(src_path)} to {dest_path}"
        except Exception as e:
            return False, str(e)

    # oprim containerul
    def stop(self):
        if self.container and self.state == "running":
            self.container.stop()
            self.refresh_status()

    # stergem containerul definitiv
    def remove(self):
        if self.container:
            try:
                self.container.remove(force=True)
                self.container = None
                self.state = "deleted"
            except Exception as e:
                print(f"Failed to remove VM {self.name}: {e}")

    # rulam comenzi in terminalul masinii virtuale
    def run_command(self, cmd, stream=False):
        if self.container and self.state == "running":
            try:
                # tratam comanda cd special pentru a pastra starea directorului
                if cmd.strip().startswith("cd "):
                    target_dir = cmd.strip()[3:].strip()
                    # verificam daca directorul exista incercand sa intram in el
                    check_cmd = f"sh -c 'cd \"{self.workdir}\" && cd \"{target_dir}\" && pwd'"
                    
                    exit_code, output = self.container.exec_run(check_cmd)
                    if exit_code == 0:
                        self.workdir = output.decode('utf-8').strip()
                        return f"Directory changed to: {self.workdir}"
                    else:
                        return f"Error changing directory: {output.decode('utf-8')}"

                # pentru comenzi normale folosim directorul curent salvat
                if stream:
                    return self.container.exec_run(cmd, stream=True, workdir=self.workdir).output
                else:
                    exit_code, output = self.container.exec_run(cmd, workdir=self.workdir)
                    return output.decode('utf-8')
            except Exception as e:
                return f"Error executing command: {e}"
        return "VM is not running"

    def apt_update(self, stream=False):
        return self.run_command("apt-get update", stream=stream)

    def install_basic_tools(self, stream=False):
        # instalam utilitare de baza precum nano (editor), procps (monitorizare), iproute2 (retea), dnsutils si wgeti 'top'
        # -iproute2: pentru comanda 'ip'
        # -dnsutils: pentru 'nslookup' si 'dig'
        # -wget: pentru descarcare fisiere
        cmd = "apt-get install -y iputils-ping net-tools curl nano procps iproute2 dnsutils wget"
        return self.run_command(cmd, stream=stream)

