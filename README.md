<div align="center">

# ☁️ Local Cloud VM Manager

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white) 
![Docker](https://img.shields.io/badge/Docker-Required-blue?style=for-the-badge&logo=docker&logoColor=white) 
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<p align="center">
  <a href="#english">🇬🇧 English</a> •
  <a href="#română">🇷🇴 Română</a>
</p>

</div>

---

<a name="english"></a>
## 🇬🇧 English

### 📝 Overview
> **Local Cloud VM Manager** is a lightweight, GUI-based application designed to manage Docker containers as if they were local Virtual Machines. It provides an intuitive interface for creating, configuring, and networking isolated environments for development and testing.

### ✨ Key Features

*   💻 **VM Management**
    *   Easily create, start, stop, and delete virtual machines (Docker containers).
*   🔧 **Resource Control**
    *   Configure **CPU** and **RAM** limits for each VM to simulate real hardware constraints.
*   🌐 **Advanced Networking**
    *   Create custom isolated networks.
    *   Connect/Disconnect VMs to/from multiple networks.
    *   Bridge mode support.
*   📂 **File Management**
    *   Upload files (tar archives) directly to running VMs.
*   ⌨️ **Terminal Integration**
    *   Open real terminals connected to your VMs.
*   🛠️ **Tools Integration**
    *   One-click installation of basic tools (`ping`, `nano`, `curl`, etc.) inside VMs.

### 🚀 Prerequisites

1.  **Python 3.8+**
2.  **Docker Desktop** (must be running).
3.  Python packages: `docker`, `tkinter` (usually included with Python).

### 📥 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ro1126/VM-Manager.git
    cd VM-Manager
    ```

2.  **Install dependencies:**
    ```bash
    pip install docker
    ```

3.  **Ensure Docker is running.**

### ▶️ Usage

Run the main application script:
```bash
python vm_manager/main.py
```

### 🏗️ Project Structure
```text
vm_manager/
├── config/         # ⚙️ Settings and constants
├── core/           # 🧠 Core logic (VM, Network, Resources)
├── docker_utils/   # 🐳 Docker client wrapper
├── gui/            # 🖥️ Tkinter User Interface
├── logs/           # 📝 Application logs
└── scripts/        # 📜 Helper scripts
```

---

<a name="română"></a>
## 🇷🇴 Română

### 📝 Prezentare Generală
> **Local Cloud VM Manager** este o aplicație ușoară cu interfață grafică (GUI), concepută pentru a gestiona containerele Docker ca și cum ar fi Mașini Virtuale locale. Oferă o interfață intuitivă pentru crearea, configurarea și conectarea mediilor izolate pentru dezvoltare și testare.

### ✨ Funcționalități Cheie

*   💻 **Gestionare VM**
    *   Creează, pornește, oprește și șterge mașini virtuale (containere Docker) cu ușurință.
*   🔧 **Control Resurse**
    *   Configurează limitele de **CPU** și **RAM** pentru fiecare VM.
*   🌐 **Rețelistică Avansată**
    *   Creează rețele izolate personalizate.
    *   Conectează/Deconectează VM-uri la/de la mai multe rețele.
    *   Suport pentru modul Bridge.
*   📂 **Gestionare Fișiere**
    *   Încarcă fișiere direct în VM-urile care rulează.
*   ⌨️ **Integrare Terminal**
    *   Deschide terminale reale conectate la VM-urile tale.
*   🛠️ **Utilitare**
    *   Instalare rapidă a uneltelor de bază (`ping`, `nano`, `curl`, etc.) în interiorul VM-urilor.

### 🚀 Cerințe

1.  **Python 3.8+**
2.  **Docker Desktop** (trebuie să fie pornit).
3.  Pachete Python: `docker`, `tkinter` (de obicei inclus în Python).

### 📥 Instalare

1.  **Clonează repository-ul:**
    ```bash
    git clone https://github.com/Ro1126/VM-Manager.git
    cd VM-Manager
    ```

2.  **Instalează dependențele:**
    ```bash
    pip install docker
    ```

3.  **Asigură-te că Docker rulează.**

### ▶️ Utilizare

Rulează scriptul principal al aplicației:
```bash
python vm_manager/main.py
```

### 🏗️ Structura Proiectului
```text
vm_manager/
├── config/         # ⚙️ Setări și constante
├── core/           # 🧠 Logică de bază (VM, Rețea, Resurse)
├── docker_utils/   # 🐳 Client Docker
├── gui/            # 🖥️ Interfață Grafică Tkinter
├── logs/           # 📝 Log-uri aplicație
└── scripts/        # 📜 Script-uri ajutătoare
```
