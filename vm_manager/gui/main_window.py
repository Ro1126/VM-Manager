from tkinter import messagebox, simpledialog, scrolledtext, filedialog
import tkinter as tk
import threading
import os
import platform
from vm_manager.core.resource_manager import ResourceManager
from vm_manager.config.settings import CONTAINER_PREFIX, DEFAULT_CPU, DEFAULT_RAM

class MainWindow:
    # initializam interfata grafica
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.root = tk.Tk()
        self.root.title("Local Cloud VM Manager")
        self.root.geometry("1000x700")
        
        # setam pictograma aplicatiei
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Failed to load icon: {e}")

        self._setup_ui()
        
        # dictionar pentru a stoca log-urile fiecarei masini virtuale
        self.vm_logs = {}
        
        self._refresh_vm_list()

    # construim elementele vizuale ale ferestrei
    def _setup_ui(self):
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(top_frame, text="Create VM", command=self._create_vm_dialog, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Refresh", command=self._refresh_vm_list).pack(side=tk.LEFT, padx=5)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        list_frame = tk.Frame(main_frame, width=250)
        list_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(list_frame, text="Virtual Machines", font=("Arial", 10, "bold")).pack()
        self.vm_listbox = tk.Listbox(list_frame, width=35, selectmode=tk.EXTENDED)
        self.vm_listbox.pack(fill=tk.Y, expand=True)
        self.vm_listbox.bind('<<ListboxSelect>>', self._on_vm_select)

        net_frame = tk.Frame(list_frame, pady=10)
        net_frame.pack(fill=tk.X)
        tk.Button(net_frame, text="Bridge Selected", command=self._bridge_selected).pack(fill=tk.X, pady=2)
        tk.Button(net_frame, text="Add to Network", command=self._add_to_network).pack(fill=tk.X, pady=2)
        tk.Button(net_frame, text="Disconnect Network", command=self._disconnect_network).pack(fill=tk.X, pady=2)
        tk.Button(net_frame, text="Delete Network", command=self._delete_network_dialog).pack(fill=tk.X, pady=2)

        details_frame = tk.Frame(main_frame)
        details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.details_label = tk.Label(details_frame, text="Select a VM to see details", justify=tk.LEFT, anchor="w", font=("Consolas", 10))
        self.details_label.pack(fill=tk.X, pady=(0, 10))

        action_frame = tk.Frame(details_frame, pady=5)
        action_frame.pack(fill=tk.X)
        
        self.btn_start = tk.Button(action_frame, text="Start", command=self._start_vm, state=tk.DISABLED, width=8)
        self.btn_start.pack(side=tk.LEFT, padx=2)
        
        self.btn_stop = tk.Button(action_frame, text="Stop", command=self._stop_vm, state=tk.DISABLED, width=8)
        self.btn_stop.pack(side=tk.LEFT, padx=2)
        
        self.btn_delete = tk.Button(action_frame, text="Delete", command=self._delete_vm, state=tk.DISABLED, width=8, fg="red")
        self.btn_delete.pack(side=tk.LEFT, padx=2)

        tools_frame = tk.Frame(details_frame, pady=5)
        tools_frame.pack(fill=tk.X)

        self.btn_update = tk.Button(tools_frame, text="Update (apt)", command=self._update_vm, state=tk.DISABLED)
        self.btn_update.pack(side=tk.LEFT, padx=2)

        self.btn_install = tk.Button(tools_frame, text="Install Tools", command=self._install_tools, state=tk.DISABLED)
        self.btn_install.pack(side=tk.LEFT, padx=2)

        self.btn_upload = tk.Button(tools_frame, text="Upload File", command=self._upload_file_dialog, state=tk.DISABLED)
        self.btn_upload.pack(side=tk.LEFT, padx=2)

        self.btn_settings = tk.Button(tools_frame, text="Resources", command=self._settings_dialog, state=tk.DISABLED)
        self.btn_settings.pack(side=tk.LEFT, padx=2)

        self.btn_terminal = tk.Button(tools_frame, text="Open Terminal", command=self._open_terminal, state=tk.DISABLED, bg="#333", fg="white")
        self.btn_terminal.pack(side=tk.LEFT, padx=2)

        cmd_frame = tk.Frame(details_frame, pady=10)
        cmd_frame.pack(fill=tk.X)
        tk.Label(cmd_frame, text="Run Command:").pack(side=tk.LEFT)
        
        self.cmd_entry = tk.Entry(cmd_frame)
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.cmd_entry.bind('<Return>', self._on_enter_command)
        self.cmd_entry.config(state=tk.DISABLED)
        
        tk.Button(cmd_frame, text="Send", command=self._on_enter_command).pack(side=tk.LEFT)

        tk.Label(details_frame, text="Output Log:").pack(anchor="w")
        self.console_output = scrolledtext.ScrolledText(details_frame, height=15, bg="black", fg="#00FF00", font=("Consolas", 10))
        self.console_output.pack(fill=tk.BOTH, expand=True)

    # reimprospatam lista de masini virtuale din interfata
    def _refresh_vm_list(self):
        self.vm_listbox.delete(0, tk.END)
        vms = self.resource_manager.get_all_vms()
        for vm in vms:
            display_name = vm.name.replace(CONTAINER_PREFIX, "")
            status_icon = "🟢" if vm.state == "running" else "🔴"
            self.vm_listbox.insert(tk.END, f"{status_icon} {display_name}")
            
            # initializam log-ul daca nu exista
            if vm.name not in self.vm_logs:
                self.vm_logs[vm.name] = ""
        
        self._update_buttons(None)
        self.details_label.config(text="Select a VM to see details")

    # cand selectam o masina virtuala din lista
    def _on_vm_select(self, event):
        selection = self.vm_listbox.curselection()
        if selection:
            index = selection[0]
            vms = self.resource_manager.get_all_vms()
            if index < len(vms):
                vm = vms[index]
                self._show_vm_details(vm)
                self._update_buttons(vm)
                
                # afisam log-ul masinii selectate
                self.console_output.delete(1.0, tk.END)
                if vm.name in self.vm_logs:
                    self.console_output.insert(tk.END, self.vm_logs[vm.name])
                self.console_output.see(tk.END)

    def _show_vm_details(self, vm):
        details = f"Name: {vm.name}\n"
        details += f"Image: {vm.image}\n"
        details += f"State: {vm.state}\n"
        details += f"IP Address: {vm.ip_address}\n"
        details += f"Resources: {vm.cpu_limit} CPU | {vm.ram_limit} RAM\n"
        self.details_label.config(text=details)

    def _update_buttons(self, vm):
        state = tk.NORMAL if vm else tk.DISABLED
        self.btn_start.config(state=state)
        self.btn_stop.config(state=state)
        self.btn_delete.config(state=state)
        self.btn_update.config(state=state)
        self.btn_terminal.config(state=state)
        self.cmd_entry.config(state=state)

        if vm:
            if vm.state == "running":
                self.btn_start.config(state=tk.DISABLED)
                self.btn_stop.config(state=tk.NORMAL)
                self.btn_upload.config(state=tk.NORMAL)
                self.btn_terminal.config(state=tk.NORMAL)
                self.btn_update.config(state=tk.NORMAL)
                self.btn_install.config(state=tk.NORMAL)
            else:
                self.btn_start.config(state=tk.NORMAL)
                self.btn_stop.config(state=tk.DISABLED)
                self.btn_update.config(state=tk.DISABLED)
                self.btn_install.config(state=tk.DISABLED)
                self.btn_upload.config(state=tk.DISABLED)
                self.btn_terminal.config(state=tk.DISABLED)
                self.cmd_entry.config(state=tk.DISABLED)

    # fereastra pentru crearea unei noi masini virtuale
    def _create_vm_dialog(self):
        name = simpledialog.askstring("Create VM", "Enter VM Name:")
        if name:
            try:
                self.resource_manager.create_vm(name)
                self._refresh_vm_list()
                self._log(f"Created VM: {name} (Default: {DEFAULT_CPU} CPU, {DEFAULT_RAM} RAM)", name)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # fereastra pentru setari resurse
    def _settings_dialog(self):
        vm = self._get_selected_vm()
        if not vm: return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Settings: {vm.name}")
        dialog.geometry("300x200")

        tk.Label(dialog, text="CPU Limit (e.g. 0.5, 1.0, 2.0):").pack(pady=5)
        cpu_entry = tk.Entry(dialog)
        cpu_entry.insert(0, str(vm.cpu_limit))
        cpu_entry.pack()

        tk.Label(dialog, text="RAM Limit (e.g. 256m, 512m, 1g):").pack(pady=5)
        ram_entry = tk.Entry(dialog)
        ram_entry.insert(0, str(vm.ram_limit))
        ram_entry.pack()

        def apply():
            try:
                cpu = float(cpu_entry.get())
                ram = ram_entry.get()
                success, msg = self.resource_manager.update_vm_resources(vm.name.replace(CONTAINER_PREFIX, ""), cpu, ram)
                if success:
                    self._log(f"Resource Update: {msg}", vm.name)
                    self._show_vm_details(vm) # Refresh UI info
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", msg)
            except ValueError:
                messagebox.showerror("Error", "Invalid CPU value")

        tk.Button(dialog, text="Apply", command=apply).pack(pady=20)

    # fereastra pentru upload fisiere
    def _upload_file_dialog(self):
        vm = self._get_selected_vm()
        if not vm: return

        file_path = filedialog.askopenfilename(title="Select file to upload")
        if file_path:
            dest_path = simpledialog.askstring("Destination", "Enter destination path in VM (folder):", initialvalue="/tmp")
            if dest_path:
                self._log(f"Uploading {file_path} to {vm.name}:{dest_path}...")
                threading.Thread(target=self._upload_thread, args=(vm, file_path, dest_path), daemon=True).start()

    def _upload_thread(self, vm, src, dest):
        success, msg = self.resource_manager.upload_file_to_vm(vm.name.replace(CONTAINER_PREFIX, ""), src, dest)
        self.root.after(0, self._log, msg, vm.name)

    # deschidem un terminal real catre vm
    def _open_terminal(self):
        vm = self._get_selected_vm()
        if not vm or vm.state != "running": return
        
        # Command to open a new terminal window and attach to the container
        container_name = vm.name
        cmd = f"docker exec -it {container_name} /bin/bash"
        
        system = platform.system()
        if system == "Windows":
            os.system(f"start cmd /k {cmd}")
        elif system == "Linux":
            os.system(f"x-terminal-emulator -e '{cmd}' || gnome-terminal -- {cmd} || xterm -e '{cmd}' &")
        elif system == "Darwin": # macOS
            os.system(f"osascript -e 'tell application \"Terminal\" to do script \"{cmd}\"'")
        
        self._log(f"Opened terminal for {vm.name}", vm.name)

    # cand dam enter in bara de comenzi
    def _on_enter_command(self, event=None):
        vm = self._get_selected_vm()
        cmd = self.cmd_entry.get()
        if vm and cmd:
            self.cmd_entry.delete(0, tk.END)
            self._start_async_command(vm, cmd, f"Running '{cmd}' on {vm.name}")

    # butonul de start
    def _start_vm(self):
        vm = self._get_selected_vm()
        if vm:
            self.resource_manager.start_vm(vm.name)
            self._refresh_vm_list()
            self._log(f"Started VM: {vm.name}", vm.name)
            # reselectam masina virtuala
            self._on_vm_select(None)

    # butonul de stop
    def _stop_vm(self):
        vm = self._get_selected_vm()
        if vm:
            self.resource_manager.stop_vm(vm.name)
            self._refresh_vm_list()
            self._log(f"Stopped VM: {vm.name}", vm.name)
            self._on_vm_select(None)

    # butonul de stergere
    def _delete_vm(self):
        vm = self._get_selected_vm()
        if vm:
            if messagebox.askyesno("Confirm", f"Delete {vm.name}?"):
                self.resource_manager.delete_vm(vm.name)
                self._refresh_vm_list()
                self._log(f"Deleted VM: {vm.name}", vm.name)

    # actualizam pachetele din vm (apt-get update)
    def _update_vm(self):
        vm = self._get_selected_vm()
        if vm:
            self._start_async_command(vm, "apt-get update", f"Updating {vm.name} (apt-get update)")

    # instalam utilitare de baza (ping, ip, nano)
    def _install_tools(self):
        vm = self._get_selected_vm()
        if vm:
            self._start_async_command(vm, "apt-get install -y iputils-ping net-tools curl", f"Installing tools on {vm.name}")

    def _start_async_command(self, vm, cmd, description):
        self._log(f"--- {description} ---", vm.name)
        thread = threading.Thread(target=self._execute_command_thread, args=(vm, cmd))
        thread.daemon = True
        thread.start()

    def _execute_command_thread(self, vm, cmd):
        try:
            # folosim stream=True pentru a primi output-ul pe masura ce este generat
            output_generator = vm.run_command(cmd, stream=True)
            
            if isinstance(output_generator, str):
                # a returnat o eroare sau un string simplu
                self.root.after(0, self._append_log, output_generator + "\n", vm.name)
            else:
                # este un generator de output
                for chunk in output_generator:
                    # chunk este in bytes deci trebuie decodat
                    text = chunk.decode('utf-8', errors='replace')
                    self.root.after(0, self._append_log, text, vm.name)
                
            self.root.after(0, self._append_log, "\n--- Command Finished ---\n", vm.name)
        except Exception as e:
            self.root.after(0, self._append_log, f"\nError: {e}\n", vm.name)

    def _append_log(self, text, vm_name=None):
        if vm_name:
            if vm_name not in self.vm_logs:
                self.vm_logs[vm_name] = ""
            self.vm_logs[vm_name] += text
            
            selected_vm = self._get_selected_vm()
            if selected_vm and selected_vm.name == vm_name:
                self.console_output.insert(tk.END, text)
                self.console_output.see(tk.END)

    # conectam vm la reteaua bridge
    def _bridge_selected(self):
        vms = self._get_selected_vms()
        if len(vms) < 2:
            messagebox.showwarning("Warning", "Select at least 2 VMs to bridge.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Bridge VMs")
        dialog.geometry("300x250")
        
        tk.Label(dialog, text="Network Name:").pack(pady=5)
        name_entry = tk.Entry(dialog)
        name_entry.pack()
        
        tk.Label(dialog, text="Subnet (e.g. 192.168.10.0/24):").pack(pady=5)
        subnet_entry = tk.Entry(dialog)
        subnet_entry.pack()
        
        def apply():
            net_name = name_entry.get()
            subnet = subnet_entry.get()
            
            if not net_name:
                messagebox.showerror("Error", "Network name is required")
                return
                
            if not subnet:
                messagebox.showerror("Error", "Subnet is required")
                return
                
            try:
                self.resource_manager.create_network(net_name, subnet)
                for vm in vms:
                    self.resource_manager.connect_vm_to_network(vm.name, net_name)
                
                self._refresh_vm_list()
                msg = f"Bridged {', '.join([v.name for v in vms])} to network '{net_name}' ({subnet})"
                for vm in vms:
                    self._log(msg, vm.name)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        tk.Button(dialog, text="Create & Bridge", command=apply).pack(pady=20)

    # adaugam vm la o retea custom
    def _add_to_network(self):
        vms = self._get_selected_vms()
        if not vms:
            messagebox.showwarning("Warning", "Select at least 1 VM.")
            return

        networks = self.resource_manager.get_available_networks()
        if not networks:
            messagebox.showinfo("Info", "No custom networks available. Create one first.")
            return

        # Simple dialog to choose network (could be improved with a Combobox dialog)
        net_str = "\n".join(networks)
        net_name = simpledialog.askstring("Select Network", f"Available Networks:\n{net_str}\n\nEnter network name:")
        
        if net_name and net_name in networks:
            for vm in vms:
                self.resource_manager.connect_vm_to_network(vm.name, net_name)
            self._refresh_vm_list()
            msg = f"Connected {', '.join([v.name for v in vms])} to '{net_name}'"
            for vm in vms:
                self._log(msg, vm.name)
        elif net_name:
            messagebox.showerror("Error", "Network not found.")
        
    # deconectam vm de la retea
    def _disconnect_network(self):
        vms = self._get_selected_vms()
        if not vms:
            messagebox.showwarning("Warning", "Select at least 1 VM.")
            return

        networks = self.resource_manager.get_available_networks()
        if not networks:
             messagebox.showinfo("Info", "No custom networks available.")
             return

        net_str = "\n".join(networks)
        net_name = simpledialog.askstring("Disconnect Network", f"Available Networks:\n{net_str}\n\nEnter network name to disconnect from:")
        
        if net_name:
            for vm in vms:
                self.resource_manager.disconnect_vm_from_network(vm.name, net_name)
            self._refresh_vm_list()
            msg = f"Disconnected {', '.join([v.name for v in vms])} from '{net_name}'"
            for vm in vms:
                self._log(msg, vm.name)

    # stergem o retea existenta
    def _delete_network_dialog(self):
        networks = self.resource_manager.get_available_networks()
        if not networks:
            messagebox.showinfo("Info", "No custom networks available.")
            return

        net_str = "\n".join(networks)
        net_name = simpledialog.askstring("Delete Network", f"Available Networks:\n{net_str}\n\nEnter network name to delete:")
        
        if net_name:
            if net_name not in networks:
                messagebox.showerror("Error", "Network not found.")
                return
                
            if messagebox.askyesno("Confirm", f"Delete network '{net_name}'?"):
                success, msg = self.resource_manager.delete_network(net_name)
                if success:
                    self._log(msg)
                else:
                    messagebox.showerror("Error", msg)

    def _get_selected_vms(self):
        selection = self.vm_listbox.curselection()
        vms = []
        all_vms = self.resource_manager.get_all_vms()
        for index in selection:
            if index < len(all_vms):
                vms.append(all_vms[index])
        return vms

    def _get_selected_vm(self):
        # returneaza prima masina virtuala selectata pentru actiuni simple
        vms = self._get_selected_vms()
        return vms[0] if vms else None

    def _log(self, message, vm_name=None):
        # daca nu specificam vm, incercam sa luam cel selectat
        if not vm_name:
            vm = self._get_selected_vm()
            if vm:
                vm_name = vm.name
        
        if vm_name:
            if vm_name not in self.vm_logs:
                self.vm_logs[vm_name] = ""
            self.vm_logs[vm_name] += message + "\n"
            
            # daca vm-ul este selectat, actualizam si interfata
            selected_vm = self._get_selected_vm()
            if selected_vm and selected_vm.name == vm_name:
                self.console_output.insert(tk.END, message + "\n")
                self.console_output.see(tk.END)

    def run(self):
        self.root.mainloop()

