from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv
import os
import argparse
import requests

class Proxmox:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("HOST")
        self.user = os.getenv("USER")
        self.token_name = os.getenv("TOKEN_NAME")
        self.token_value = os.getenv("TOKEN_VALUE")

        if not all([self.host,self.user,self.token_name,self.token_value]):
            raise ValueError("Error: Insufficient Credentials! Please enter them in .env")
        
        self.proxmox = ProxmoxAPI(
            host=self.host,
            user=self.user,
            token_name=self.token_name,
            token_value=self.token_value,
            verify_ssl=False,
            timeout=10,
        )
        
    def list_resource(self, node_name=None, resource: str | list | tuple | None = None):
        try:
            if resource:
                if isinstance(resource, (list, tuple)):
                    combined_resources = []
                    for res in resource:
                        data = self.list_resource(node_name=node_name, resource=res)
                        if isinstance(data, list):
                            combined_resources.extend(data)
                    return combined_resources
                if resource == "nodes":
                    return self.proxmox("nodes").get()
                if node_name:
                    node_api = self.proxmox.nodes(node_name)
                    resource_api = getattr(node_api, resource)
                    return resource_api.get()
                else:
                    nodes_list = self.list_resource(resource="nodes")
                    combined = []
                    if isinstance(nodes_list, list):
                        for node in (nodes_list or []):
                            if isinstance(node, dict):
                                name = node['node']
                                try:
                                    node_api = self.proxmox.nodes(name)
                                    resource_api = getattr(node_api, resource)
                                    data = resource_api.get()
                                    combined.extend(data)
                                except Exception:
                                    continue
                        return combined
        except requests.exceptions.Timeout:
            raise ConnectionError("Error: Connection Timed out")
        except Exception as e:
            raise RuntimeError(f"Error: {e}")

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
        cluster = Proxmox()
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
        for node in (cluster.list_resource(node_name=args.node_name, resource="nodes") or []):
            node_name_string = node.get('node')
            status = node.get('status', 'N/A')
            if not args.node_name or (args.node_name.lower() in node_name_string.lower()):
                print(f"Node: {node_name_string} | Status: {status}")
    if args.vm:
        print("\n====================")
        print(f"Virtual Machines{f' on {args.node_name}' if args.node_name else ''}:")
        print("====================")
        for vm in (cluster.list_resource(node_name=args.node_name, resource="qemu") or []):
            name = vm.get('name', 'N/A')
            vmid = vm.get('vmid', 'N/A')
            status = vm.get('status', 'N/A')
            ram_mb = vm.get('maxmem', 0) // (1024 * 1024)

            print(f"ID: {vmid} | Name: {name} | Status: {status} | RAM: {ram_mb}MB")

    if args.lxc:
        print("\n====================")
        print(f"LXC Containers{f' on {args.node_name}' if args.node_name else ''}:")
        print("====================")
        for lxc in (cluster.list_resource(node_name=args.node_name, resource="lxc") or []):
            
            name = lxc.get('name', 'N/A')
            vmid = lxc.get('vmid', 'N/A')
            status = lxc.get('status', 'N/A')
            ram_mb = lxc.get('maxmem', 0) // (1024 * 1024)

            print(f"ID: {vmid} | Name: {name} | Status: {status} | RAM: {ram_mb}MB")

            


if __name__ == "__main__":
    main()
