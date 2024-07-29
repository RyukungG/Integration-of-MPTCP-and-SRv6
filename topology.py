import os
import subprocess
from time import sleep
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSBridge
from mininet.log import info
from mininet.link import TCLink
from base_node import HostNode, Router
from FRR import FRR

class MyMininet():
    def __init__(self):
        self.net = Mininet(switch=OVSBridge)
        self.hosts = {}
        self.routers = {}
        self.links = {}

    def get_node_name_from_interface(self, interface: str):
        for key, value in self.links.items():
            for link in value:
                if link['intfName'] == interface:
                    return key
        return None

    def addNode(self, name, **kwargs):
        host = self.net.addHost(name, ip=None, cls=HostNode)
        self.hosts[name] = host
        return host
    
    def addRouter(self, name, **kwargs):
        router = self.net.addHost(name, ip=None, cls=Router)
        self.routers[name] = router
        return router
    
    def addRouterFRR(self, name, **kwargs):
        router = self.net.addHost(name, ip=None, cls=FRR)
        self.routers[name] = router
        return router

    def link(self, node1, node2,
             intfName1: str=None, intfName2: str=None,
             **kwargs):
        edge = self.net.addLink(node1, node2, 
                                intfName1=intfName1, 
                                intfName2=intfName2,
                                cls=TCLink,
                                **kwargs)
        return edge

    def setLinkIPv4(self, edge, 
                    ipv4_1: str, ipv4_2: str,
                    gateway1: str=None, gateway2: str=None,
                    mtu: int=3000, metric: int=100):
        interface1 = edge.intf1
        interface2 = edge.intf2
        interface1.node.setIPv4(ipv4_1, intf=interface1.name, gateway=gateway1, mtu=mtu, metric=metric)
        interface2.node.setIPv4(ipv4_2, intf=interface2.name, gateway=gateway2, mtu=mtu, metric=metric)

        for i in range(1, 3):
            if self.links.get(eval(f'interface{i}.node.name')) is None:
                self.links[eval(f'interface{i}.node.name')] = []
            self.links[eval(f'interface{i}.node.name')].append({'intfName': eval(f'interface{i}.name'), 'ipv4': eval(f'ipv4_{i}')})


    def setLinkIPv6(self, edge,
                    ipv6_1: str, ipv6_2: str,
                    gateway1: str=None, gateway2: str=None,
                    mtu: int=3000, metric: int=100):
        interface1 = edge.intf1
        interface2 = edge.intf2
        interface1.node.setIPv6(ipv6_1, intf=interface1.name, gateway=gateway1, mtu=mtu, metric=metric)
        interface2.node.setIPv6(ipv6_2, intf=interface2.name, gateway=gateway2, mtu=mtu, metric=metric)

        for i in range(1, 3):
            if self.links.get(eval(f'interface{i}.node.name')) is None:
                self.links[eval(f'interface{i}.node.name')] = []
            self.links[eval(f'interface{i}.node.name')].append({'intfName': eval(f'interface{i}.name'), 'ipv6': eval(f'ipv6_{i}')})
    
    def setFRR(self, mtu: int = 3000):
        id = 1
        for key, val in self.links.items():
            if key in self.hosts.keys():
                print(f'{key} is a host')
                continue
            conf = f'''\
enable
configure terminal
router ospf6
ospf6 router-id {id}.{id}.{id}.{id}
exit
'''
            for link in val:
                conf += f'''\
interface {link['intfName']}
ipv6 ospf6 area 0.0.0.0
ipv6 ospf6 ifmtu {mtu}
exit
''' 

            conf += f'''\
segment-routing
srv6
locators
'''
            locator_id = 1
            for link in val:
                conf += f'''\
locator loc{locator_id}
prefix {':'.join(link['ipv6'].split(':')[:-1])+':'}/64
exit
'''
                locator_id += 1

            conf += f'''\
exit
exit
'''
            self.routers[key].vtysh_cmd(conf)
            id += 1

    def setBandwidth(self, intfs: list[str], bandwidth: int):
        for intf in intfs:
            rid = 0
            for r in intf.split('-'):
                intf_name = f"{intf.split('-')[rid]}-{intf.split('-')[rid-1]}"
                self.routers[self.get_node_name_from_interface(intf_name)].intf(intf_name).config(bw=bandwidth)
                rid -= 1

    def setAllMTUs(self, mtu: int = 3000):
        for node in list(self.hosts.values()) + list(self.routers.values()):
            node.setAllMTUs(mtu)

    def iperf(self, client, server, duration: int=10, logfolder: str="log", mptcp: bool=False, testtime: int=1):
        nodes = self.hosts | self.routers
        if mptcp:
            mptcp_prefix = 'mptcpize run '
        else:
            mptcp_prefix = ''
        nodes[server[0]].cmd(f'{mptcp_prefix}iperf3 -s -V --logfile ./Log/{logfolder}/iperf_server.txt &')
        for _ in range(testtime):
            print(_, 'Test')
            nodes[client[0]].cmd(f'{mptcp_prefix}iperf3 -c {server[1]} -t {duration} -V --logfile ./Log/{logfolder}/iperf_client.txt')
            sleep(10)
        print(f'{mptcp_prefix}iperf3 -s -V --logfile ./Log/{logfolder}/iperf_server.txt &')
        print(f'{mptcp_prefix}iperf3 -c {server[1]} -t {duration} -V --logfile ./Log/{logfolder}/iperf_client.txt')
        nodes[server[0]].cmd('killall iperf3')

    def start(self):
        self.net.start()

    def startCLI(self):
        CLI(self.net)

    def stop(self):
        self.net.stop()

class DumpData():
    def __init__(self, mininet, dirName):
        self.mininet = mininet
        self.dirName = dirName
        self.processes = []

        # Ensure dump directory exists
        if not os.path.exists(f'./{self.dirName}'):
            os.makedirs(f'./{self.dirName}')

    def dump(self):
        procress = subprocess.Popen(['tcpdump', '-i', 'any', '-d', 'ip6 and tcp', '-w', f'./{self.dirName}/dump.pcap'])
        self.processes.append(procress)
            
    def dumpNode(self):
        # Run tcpdump on each node
        for node in list(self.mininet.hosts.values()) + list(self.mininet.routers.values()):
            procress = node.tcpdump(self.dirName)
            self.processes.append(procress)

    def terminate(self):
        for process in self.processes:
            process.terminate()