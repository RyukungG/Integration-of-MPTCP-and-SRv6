from subprocess import Popen
from typing import List
from mininet.node import Node, Host
from mininet.log import logging


def LoggedNode(log = True , based: type[Node] | type[Host] = Node):
    if log:
        class _Node(based):
            def cmd(self: Node | Host, *args, **kwargs):
                res = super().cmd(*args, **kwargs)
                # logging.info('\n')
                # logging.info(f'{self.name}:', '\n', *args , '\n')
                # logging.info(f'{self.name}:', '\n', res , '\n\n')
                return res
            
            def popen(self, *args, **kwargs) -> Popen[str]:
                res = super().popen(*args, **kwargs)
                # logging.info('\n')
                # logging.info(f'{self.name}:', '\n', *args , '\n')
                # logging.info(f'{self.name}:', '\n', res , '\n\n')
                return res       
        return _Node
    return based

class HostNode(LoggedNode(based=Host)):

    PRIVATEDIRS = ["/etc/iproute2"]

    def __init__(self, name, inNamespace=True, **params):
        params.setdefault("privateDirs", [])
        params["privateDirs"].extend(self.PRIVATEDIRS)
        super().__init__(name, inNamespace, **params)
        self.start_ssh()

    def config(self, **params):
        super(HostNode, self).config(**params)
        self.cmd('ifconfig lo up')
        self.cmd('sysctl -w net.core.optmem_max=512000')
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.mptcp.enabled=1')
        self.cmd('sysctl -w net.mptcp.checksum_enabled=1')
        self.cmd('sysctl -w net.ipv4.tcp_mtu_probing=1')
        self.cmd("sysctl -w net.ipv4.conf.all.rp_filter=0")
        self.cmd("sysctl -w net.ipv6.conf.all.forwarding=1")
        self.cmd("sysctl -w net.ipv6.conf.all.seg6_enabled=1")
        self.cmd("sysctl -w net.ipv6.seg6_flowlabel=1")
        self.cmd("sysctl -w net.ipv6.conf.all.seg6_require_hmac=0")
        self.cmd("sysctl -w net.ipv6.conf.all.accept_ra_pmtu=1")
        self.cmd("sysctl -w net.ipv6.conf.all.accept_redirects=1")

        for i in self.nameToIntf.keys():
            self.cmd("sysctl -w net.ipv6.conf.{}.seg6_enabled=1".format(i))


    def setIPv6(self, ip: str , intf: str = None , gateway: str = None, mtu: int = 3000, metric: int = 100):
        self.cmd(f'ip -6 addr add {ip} dev {intf}')
        if gateway is not None:
            self.cmd(f'ip -6 route add default dev {intf} via {gateway} metric {metric}')
        self.setMTUs('-6', intf, mtu)
    
    def setIPv4(self, ip: str, intf: str = None, gateway: str = None, mtu: int = 3000, metric: int = 100):
        self.cmd(f'ip -4 addr add {ip} dev {intf}')
        if gateway is not None:
            self.cmd(f'ip -4 route add default dev {intf} via {gateway} metric {metric}')
        self.setMTUs('-4', intf, mtu)
    
    def start_ssh(self):
        return self.cmd('/usr/sbin/sshd -D&')
    
    def tcpdump(self, dirName: str = 'dump'):
        return self.popen(f'tcpdump -i any -d tcp -w ./{dirName}/{self.name}.pcap')
    
    def setMTUs(self, ip: str,intf: str, mtu: int = 3000):
        self.cmd(f'ip {ip} link set dev {intf} mtu {mtu}')

    def setAllMTUs(self, mtu: int = 3000):
        self.cmd(f'sysctl -w net.ipv6.conf.all.mtu={mtu}')
        self.cmd(f'sysctl -w net.ipv6.conf.default.mtu={mtu}')
        self.cmd(f'iptables -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss {mtu-300}')
        self.cmd(f'ip6tables -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss {mtu-300}')
    
    def write_sysctl(self, key, value):
        self.cmd('sysctl -w {}={}'.format(key, value), shell=True)

class Router(LoggedNode(based=HostNode)):

    def __init__(self, name, **params):
        super().__init__(name, **params)
    
    def config(self, **params):
        super(Router, self).config(**params)
    
    def addDefaultV4Route(self, via: str , intf: str, metric: int):
        self.cmd(f'ip -4 route add default via {via} dev {intf} metric {metric}')

    def addDefaultV6Route(self, via: str , intf: str, metric: int):
        self.cmd(f'ip -6 route add default via {via} dev {intf} metric {metric}')

    def addStaticV4Route(self, target: str , via: str , intf: str):
        self.cmd(f'ip -4 route add {target} via {via} dev {intf}')
    
    def addStaticV6Route(self, target: str , via: str , intf: str):
        self.cmd(f'ip -6 route add {target} via {via} dev {intf}')

    def addSRv6Route(self, target: str , via: List[str], intf: str):
        print(f'ip -6 route add {target} encap seg6 mode encap segs {",".join(via)} dev {intf}')
        self.cmd(f'ip -6 route add {target} encap seg6 mode encap segs {",".join(via)} dev {intf}')

