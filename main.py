import os
from  dotenv import load_dotenv
from proxmoxer import ProxmoxAPI
import argparse
import requests

class ProxmoxCluster:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("HOST")
        self.user = os.getenv("USER")
        self.token_name = os.getenv("TOKEN_NAME")
        self.token_value = os.getenv("TOKEN_VALUE")

        if not all([self.host, self.user, self.token_name, self.token_value]):
            raise ValueError("Error: Missing required values, please check or create a .env")

        self.proxmox = ProxmoxAPI(
            host=self.host,
            user=self.user,
            token_name=self.token_name,
            token_value=self.token_value,
            verify_ssl=False,
            timeout = 30,
        )
    def list_nodes(self):
        try:
            nodes_data = self.proxmox("nodes").get()
            if not nodes_data:
                print("Warning: Proxmox API returned no node data.")
                return []
            return [f"Node: {node['node']} - Status: {node['status']}" for node in nodes_data]
        except requests.exceptions.ReadTimeout:
            return ["Error: Proxmox took too long it timed out. Check if node is offline or try again."]
        except Exception as e:
            return [f"Error: {e}"]
    def list_vms(self, target_node=None):
        try:
            if target_node:
                nodes_data = [{'node': target_node}]
            else:
                nodes_data = self.proxmox("nodes").get()
            if not nodes_data:
                return ["No nodes available to query VMs."]
            
            vm_list = []
            for node in nodes_data:
                node_name = node['node']
                try:
                    vms = self.proxmox.nodes(node_name).qemu.get()
                    for vm in (vms or []):
                        vm_list.append(
                            f"Node: {node_name} | Status: {vm.get('status')} | "
                            f"Name: {vm.get('name', 'N/A')} | VMID: {vm.get('vmid')} | "
                            f"CPU Cores: {vm.get('cpus', 'N/A')} | RAM: {vm.get('maxmem', 0) // (1024*1024)}MB"
                        )
                except Exception:
                    continue # Skip node if query fails
                    
            return vm_list if vm_list else ["No VMs detected!."]
        except requests.exceptions.ReadTimeout:
            return ["Error: Proxmox request timed out while fetching VMs."]
        except Exception as e:
            return [f"Error: {e}"]

    def list_lxc(self, target_node=None):
        try:
            if target_node:
                nodes_data = [{'node': target_node}]
            else:
                nodes_data = self.proxmox("nodes").get()
            if not nodes_data:
                return ["No nodes available to query LXC containers."]
            lxc_list = []
            for node in nodes_data:
                node_name = node['node']
                try:
                    cts = self.proxmox.nodes(node_name).lxc.get()
                    for container in (cts or []):
                        lxc_list.append(
                            f"Node: {node_name} | Status: {container.get('status')} | "
                            f"Name: {container.get('name', 'N/A')} | CTID: {container.get('vmid')} | "
                            f"RAM: {container.get('maxmem', 0) // (1024*1024)}MB"
                        )
                except Exception:
                    continue
            return lxc_list if lxc_list else ["No LXCs detected!"]
        except requests.exceptions.ReadTimeout:
            return ["Error: Proxmox request timed out while fetching containers."]
        except Exception as e:
            return [f"Error: {e}"]

def main():
    parser = argparse.ArgumentParser(description="Proxmox Monitoring Script")
    parser.add_argument('--nodes', action="store_true", help='List all nodes')
    parser.add_argument('--node-name', type=str, help='Targets a specfic node')
    parser.add_argument('--vm', action="store_true", help='List all VMs')
    parser.add_argument('--lxc', action="store_true", help='List all LXCs')
    parser.add_argument('--all', action="store_true", help='List nodes, LXCs')
    args = parser.parse_args()
    if args.all or not (args.nodes or args.vm or args.lxc):
        args.nodes = args.vm = args.lxc = True
    try:
        cluster = ProxmoxCluster()
    except Exception as e:
        print(f"Failed to connect to Proxmox API: {e}")
        return
    if args.nodes:
        print("\n====================")
        if args.node_name:
            print(f"Target Node Status ({args.node_name}):")
        else:
            print("Nodes in the Proxmox cluster:")
        print("====================")
        for node in cluster.list_nodes():
            if not args.node_name or args.node_name.lower() in node.lower():
                print(node)
    if args.vm:
        print("\n====================")
        print(f"Virtual Machines{f' on {args.node_name}' if args.node_name else ''}:")
        print("====================")
        for vm in cluster.list_vms(target_node=args.node_name):
            print(vm)
    if args.lxc:
        print("\n====================")
        print(f"LXC Containers{f' on {args.node_name}' if args.node_name else ''}:")
        print("====================")
        for lxc in cluster.list_lxc(target_node=args.node_name):
            print(lxc)

        

if __name__ == "__main__":
    main()

