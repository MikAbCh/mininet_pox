from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, OVSSwitch

class SimpleHubTopo(Topo):
    def build(self):
        switch = self.addSwitch('s1')
        for h in range(1, 6):
            host = self.addHost(f'h{h}')
            self.addLink(host, switch)

def run():
    topo = SimpleHubTopo()

    # Gunakan RemoteController dan tentukan protokol OpenFlow10
    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633),
        autoSetMacs=True,
        autoStaticArp=True
    )

    # Atur protokol OpenFlow10 secara eksplisit untuk switch
    for sw in net.switches:
        sw.cmd('ovs-vsctl set Bridge {} protocols=OpenFlow10'.format(sw.name))

    net.start()

    info("*** Jalankan ping dari h1 ke h2 dan h5\n")
    h1, h2, h5 = net.get('h1', 'h2', 'h5')
    print(h1.cmd('ping -c 4 10.0.0.2'))
    print(h1.cmd('ping -c 4 10.0.0.5'))

    info("*** Jalankan iperf antara h1 dan h2 serta h1 dan h5\n")
    print(h2.cmd('iperf -s &'))
    print(h5.cmd('iperf -s &'))
    print(h1.cmd('iperf -c 10.0.0.2'))
    print(h1.cmd('iperf -c 10.0.0.5'))

    info("*** Jalankan pingall\n")
    print(net.pingAll())

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
