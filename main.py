from time import sleep
from mininet.log import setLogLevel
from topology import MyMininet, DumpData

def createMininet(mtus: int=1500):
    PREFIX = 'fd00:0:'

    setLogLevel('info')
    net = MyMininet()

    # Creating nodes in the network
    h1 = net.addNode('h1')
    h2 = net.addNode('h2')
    r1 = net.addRouterFRR('r1')
    r2 = net.addRouterFRR('r2')
    r3 = net.addRouterFRR('r3')
    r4 = net.addRouterFRR('r4')
    r5 = net.addRouterFRR('r5')
    r6 = net.addRouterFRR('r6')
    
    # Creating links between nodes
    h1_r1 = net.link(h1, r1,
                        intfName1='h1-r1',
                        intfName2='r1-h1')
    h1_r3 = net.link(h1, r3,
                        intfName1='h1-r3',
                        intfName2='r3-h1')
    
    h2_r4 = net.link(h2, r4,
                        intfName1='h2-r4',
                        intfName2='r4-h2')
    h2_r6 = net.link(h2, r6,
                        intfName1='h2-r6',
                        intfName2='r6-h2')
    
    r1_r4 = net.link(r1, r4,
                        intfName1='r1-r4',
                        intfName2='r4-r1',
                        bw=100, delay='30ms')
    r2_r5 = net.link(r2, r5,
                        intfName1='r2-r5',
                        intfName2='r5-r2',
                        bw=200, delay='30ms')
    r3_r6 = net.link(r3, r6,
                        intfName1='r3-r6',
                        intfName2='r6-r3',
                        bw=100, delay='30ms')
    
    r1_r2 = net.link(r1, r2,
                        intfName1='r1-r2',
                        intfName2='r2-r1',
                        bw=200, delay='30ms')
    r2_r3 = net.link(r2, r3,
                        intfName1='r2-r3',
                        intfName2='r3-r2',
                        bw=200, delay='30ms')
    r4_r5 = net.link(r4, r5,
                        intfName1='r4-r5',
                        intfName2='r5-r4',
                        bw=200, delay='30ms')
    r5_r6 = net.link(r5, r6,
                        intfName1='r5-r6',
                        intfName2='r6-r5',
                        bw=200, delay='30ms')
    
    
    # Configure IPv6
    net.setLinkIPv6(h1_r1, PREFIX + '1:1::10/64', PREFIX + '1:1::1/64',
                    gateway1=PREFIX + '1:1::1', metric=100, mtu=mtus)
    net.setLinkIPv6(h1_r3, PREFIX + '1:3::10/64', PREFIX + '1:3::1/64',
                    gateway1=PREFIX + '1:3::1', metric=200, mtu=mtus)
    
    net.setLinkIPv6(h2_r4, PREFIX + '2:1::10/64', PREFIX + '2:1::1/64',
                    gateway1=PREFIX + '2:1::1', metric=100, mtu=mtus)
    net.setLinkIPv6(h2_r6, PREFIX + '2:3::10/64', PREFIX + '2:3::1/64',
                    gateway1=PREFIX + '2:3::1', metric=200, mtu=mtus)
    
    net.setLinkIPv6(r1_r4, PREFIX + 'a:1::1/64', PREFIX + 'a:1::4/64', mtu=mtus)
    net.setLinkIPv6(r2_r5, PREFIX + 'b:1::2/64', PREFIX + 'b:1::5/64', mtu=mtus)
    net.setLinkIPv6(r3_r6, PREFIX + 'c:1::3/64', PREFIX + 'c:1::6/64', mtu=mtus)

    net.setLinkIPv6(r1_r2, PREFIX + 'ab:1::1/64', PREFIX + 'ab:1::2/64', mtu=mtus)
    net.setLinkIPv6(r4_r5, PREFIX + 'ab:2::4/64', PREFIX + 'ab:2::5/64', mtu=mtus)
    net.setLinkIPv6(r2_r3, PREFIX + 'bc:1::2/64', PREFIX + 'bc:1::3/64', mtu=mtus)
    net.setLinkIPv6(r5_r6, PREFIX + 'bc:2::5/64', PREFIX + 'bc:2::6/64', mtu=mtus)

    net.setAllMTUs(mtus)
    
    # Configure SRv6
    # r1.addSRv6Route("fd00:0:2:1::/64",["fd00:0:b:1::5"] ,"r1-r2")
    # r4.addSRv6Route("fd00:0:1:1::/64",["fd00:0:b:1::2"] ,"r4-r5")

    # Conifgure routing tables for MPTCP
    h1.cmd('echo "1 101" >> /etc/iproute2/rt_tables')
    h1.cmd('echo "2 102" >> /etc/iproute2/rt_tables')
    h1.cmd('echo "3 103" >> /etc/iproute2/rt_tables')

    h1.cmd('ip -6 rule add from fd00:0:1:1::10 table 101')
    h1.cmd('ip -6 route add default via fd00:0:1:1::1 dev h1-r1 table 101')
    h1.cmd('ip -6 rule add from fd00:0:1:2::10 table 102')
    h1.cmd('ip -6 route add default via fd00:0:1:2::1 dev h1-r2 table 102')
    h1.cmd('ip -6 rule add from fd00:0:1:3::10 table 103')
    h1.cmd('ip -6 route add default via fd00:0:1:3::1 dev h1-r3 table 103')
    
    h2.cmd('echo "1 101" >> /etc/iproute2/rt_tables')
    h2.cmd('echo "2 102" >> /etc/iproute2/rt_tables')
    h2.cmd('echo "3 103" >> /etc/iproute2/rt_tables')

    h2.cmd('ip -6 rule add from fd00:0:2:1::10 table 101')
    h2.cmd('ip -6 route add default via fd00:0:2:1::1 dev h2-r7 table 101')
    h2.cmd('ip -6 rule add from fd00:0:2:2::10 table 102')
    h2.cmd('ip -6 route add default via fd00:0:2:2::1 dev h2-r8 table 102')
    h2.cmd('ip -6 rule add from fd00:0:2:3::10 table 103')
    h2.cmd('ip -6 route add default via fd00:0:2:3::1 dev h2-r9 table 103')

    # Configure MPTCP
    h1.cmd("ip -6 mptcp limits set subflows 1 add_addr_accepted 1")
    # h1.cmd("ip -6 mptcp endpoint add fd00:0:1:2::10 dev h1-r2 subflow")
    h1.cmd("ip -6 mptcp endpoint add fd00:0:1:3::10 dev h1-r3 subflow fullmesh")
    # h1.cmd("ip -6 mptcp endpoint add fd00:0:1:1::10 dev h1-r1 subflow")

    h2.cmd("ip -6 mptcp limits set subflows 1 add_addr_accepted 1")
    h2.cmd("ip -6 mptcp endpoint add fd00:0:2:1::10 dev h2-r4 signal")
    # h2.cmd("ip -6 mptcp endpoint add fd00:0:2:2::10 dev h2-r5 signal")
    h2.cmd("ip -6 mptcp endpoint add fd00:0:2:3::10 dev h2-r6 signal")

    return net

def run():
    net = createMininet(3000)
    
    net_dump = DumpData(net, 'dump_main')
    net_dump.dumpNode()

    net.start()

    net.setFRR(3000)
    # sleep(60)
    # net.iperf(['h1', 'fd00:0:1:1::10'], ['h2', 'fd00:0:2:1::10'], duration=60, mptcp=False, logfolder='tcp_log_without_srv6', testtime=5)
    net.startCLI()

    net_dump.terminate()
    net.stop()

if __name__ == '__main__':
    run()