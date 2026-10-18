# Proxmox Cluster Monitoring Script

A lightweight, command-line Python utility designed to monitor your Proxmox VE homelab cluster infrastructure. It authenticates securely using API tokens and provides flexible CLI filtering to inventory physical compute nodes, QEMU virtual machines, and LXC containers cluster-wide or on a specific target node.

---

## Features

* **Cluster-Wide & Node-Specific Discovery:** Inspect all physical nodes, VMs, and containers across your entire cluster, or target a single node name.
* **Token-Based Authentication:** Securely connects via Proxmox API tokens managed through environment variables (`.env`).
* **Robust Error Handling:** Handles connection timeouts and API drops gracefully to prevent execution crashes.
* **Flexible CLI Arguments:** Built with `argparse` for quick custom filtering straight from your terminal.

---

## 1. Prerequisites & Installation

Make sure you have Python installed on your system. Place your `main.py` script into a local project directory, then install the required third-party dependencies:

```bash
pip install proxmoxer python-dotenv requests
```

---

## 2. Configuration (`.env`)

Create a file named `.env` in the exact same directory as your `main.py` script. Populate it with your Proxmox API credentials and host details:

```env
HOST=192.168.1.x
USER=root@pam
TOKEN_NAME=proxmox_monitor_cli
TOKEN_VALUE=your-uuid-secret-token-here
```

---

## 3. Usage & Examples

Run the script from your terminal using Python. If no flags are passed, it defaults to showing everything (`--all`).

### Run Everything (Default)
Queries all nodes, virtual machines, and LXC containers across the entire cluster:
```bash
python main.py
```

### View Only Physical Nodes
```bash
python main.py --nodes
```

### View Only Virtual Machines (VMs)
```bash
python main.py --vm
```

### View Only LXC Containers
```bash
python main.py --lxc
```

### Target a Specific Node
You can filter any query to target a single physical node (e.g., `legion5`, `intelNUC`, `hpelitedeskg6800`) using `--node-name`:

```bash
python main.py --vm --node-name legion5
```
```bash
python main.py --lxc --node-name intelNUC
```
```bash
python main.py --nodes --node-name hpelitedeskg6800
```

---

## 4. Command-Line Arguments Reference

| Option | Description |
| :--- | :--- |
| `--nodes` | Lists physical cluster nodes and their online/offline status. |
| `--vm` | Lists QEMU virtual machines (includes node, status, name, VMID, CPU cores, and RAM). |
| `--lxc` | Lists LXC containers (includes node, status, name, CTID, and RAM). |
| `--all` | Displays nodes, VMs, and LXCs (default behavior if no flags are passed). |
| `--node-name <name>` | Filters the output down to a specific compute node. |
