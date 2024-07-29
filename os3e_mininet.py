from time import sleep
from mininet.log import setLogLevel
from topology import MyMininet, DumpData
from os3e import OS3E

def createMininet(mtus: int=1500):
    setLogLevel('info')
    net = MyMininet()
    os3e = OS3E()
    os3e_routers = os3e.get_router()
    os3e_links = os3e.get_link()

    # Display the DataFrames
    print("Router DataFrame:")
    print(os3e_routers)
    print("\nLink DataFrame:")
    print(os3e_links)

    routers = {}
    links = {}

    # Creating nodes in the network
    for i in range(len(os3e_routers)):
        router_name = os3e_routers.loc[i, 'node']
        routers[router_name] = net.addRouterFRR(router_name)
    
    for i in range(len(os3e_links)):
        link = net.link(routers[os3e_links.loc[i, 'source']],
                        routers[os3e_links.loc[i, 'dest']],
                        intfName1=os3e_links.loc[i, 'source'][0:3]+'-'+os3e_links.loc[i, 'dest'][0:3],
                        intfName2=os3e_links.loc[i, 'dest'][0:3]+'-'+os3e_links.loc[i, 'source'][0:3],
                        bw=200, delay=str(os3e_links.loc[i, 'delay']*1000)+'ms')
        links[os3e_links.loc[i, 'ipv6']] = link

    # Configure IPv6
    for ip, val in links.items():
        net.setLinkIPv6(val, ip+'1/64', ip+'2/64', mtu=mtus)

    net.setAllMTUs(mtus)

    # Configure IPv6 addresses
    routers['Seattle'].addDefaultV6Route('fd00:0:42::1', 'Sea-Por', 200)
    routers['Seattle'].addDefaultV6Route('fd00:0:41::1', 'Sea-Sal', 500)
    routers['Seattle'].addDefaultV6Route('fd00:0:33::1', 'Sea-Mis', 1000)

    routers['Chicago'].addDefaultV6Route('fd00:0:5::2', 'Chi-Ind', 200)
    routers['Chicago'].addDefaultV6Route('fd00:0:6::2', 'Chi-Kan', 500)
    routers['Chicago'].addDefaultV6Route('fd00:0:7::2', 'Chi-Min', 1000)

    # Conifgure routing tables for MPTCP
    seattle_cmd = ['echo "1 101" >> /etc/iproute2/rt_tables',
                   'echo "2 102" >> /etc/iproute2/rt_tables',
                   'echo "2 103" >> /etc/iproute2/rt_tables',
                   'ip -6 rule add from fd00:0:42::2 table 101',
                   'ip -6 rule add from fd00:0:41::2 table 102',
                   'ip -6 rule add from fd00:0:33::2 table 103',
                   'ip -6 route add default via fd00:0:42::1 dev Sea-Por table 101',
                   'ip -6 route add default via fd00:0:41::1 dev Sea-Sal table 102',
                   'ip -6 route add default via fd00:0:33::1 dev Sea-Mis table 103']
    
    for cmd in seattle_cmd:
        routers['Seattle'].cmd(cmd)

    chicago_cmd = ['echo "1 101" >> /etc/iproute2/rt_tables',
                   'echo "2 102" >> /etc/iproute2/rt_tables',
                   'echo "2 103" >> /etc/iproute2/rt_tables',
                   'ip -6 rule add from fd00:0:5::1 table 101',
                   'ip -6 rule add from fd00:0:6::1 table 102',
                   'ip -6 rule add from fd00:0:7::1 table 103',
                   'ip -6 route add default via fd00:0:5::2 dev Chi-Ind table 101',
                   'ip -6 route add default via fd00:0:6::2 dev Chi-Kan table 101',
                   'ip -6 route add default via fd00:0:7::2 dev Chi-Min table 102']
    
    for cmd in chicago_cmd:
        routers['Chicago'].cmd(cmd)

    # Configure SRv6
    routers['Seattle'].addSRv6Route('fd00:0:6::/64', ['fd00:0:41::1'], 'Sea-Sal')
    # routers['Seattle'].addSRv6Route('fd00:0:5::/64', ['fd00:0:42::1', 'fd00:0:36::1','fd00:0:25::2'], 'Sea-Por')

    routers['Chicago'].addSRv6Route('fd00:0:41::/64', ['fd00:0:6::2'], 'Chi-Kan')
    # routers['Chicago'].addSRv6Route('fd00:0:42::/64', ['fd00:0:5::2', 'fd00:0:21::1','fd00:0:3::2'], 'Chi-Ind')

    # Configure MPTCP
    routers['Seattle'].cmd("ip -6 mptcp limits set subflows 2 add_addr_accepted 1")
    # routers['Seattle'].cmd("ip -6 mptcp endpoint add fd00:0:42::2 dev Sea-Por subflow fullmesh")
    routers['Seattle'].cmd("ip -6 mptcp endpoint add fd00:0:41::2 dev Sea-Sal subflow fullmesh")
    routers['Seattle'].cmd("ip -6 mptcp endpoint add fd00:0:33::2 dev Sea-Mis subflow fullmesh")

    routers['Chicago'].cmd("ip -6 mptcp limits set subflows 2 add_addr_accepted 1")
    # routers['Chicago'].cmd("ip -6 mptcp endpoint add fd00:0:5::1 dev Chi-Ind signal")
    routers['Chicago'].cmd("ip -6 mptcp endpoint add fd00:0:6::1 dev Chi-Kan signal")
    routers['Chicago'].cmd("ip -6 mptcp endpoint add fd00:0:7::1 dev Chi-Min signal")

    return net

def run():
    intfs_top = ['Sea-Mis', 'Mis-Min', 'Min-Chi']
    net = createMininet(9000)
    net.setBandwidth(intfs_top, 100)

    net.start()

    net.setFRR(9000)
    
    sleep(60)
    net.iperf(['Seattle', 'fd00:0:41::2'], ['Chicago', 'fd00:0:6::1'], duration=60, mptcp=False, logfolder='os3e/tcp_log_with_srv6', testtime=5)

    # net.startCLI()

    net.stop()

if __name__ == '__main__':
    run()