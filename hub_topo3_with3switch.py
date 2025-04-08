from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, OVSSwitch

class CustomHubTopo(Topo):
    def build(self):
        # Tambahkan switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Tambahkan host
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')

        # Hubungkan host ke switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)

        self.addLink(s1, s2)
        self.addLink(s2, s3)

        self.addLink(h3, s3)
        self.addLink(h4, s3)
        self.addLink(h5, s3)

def run():
    topo = CustomHubTopo()
    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633),
        autoSetMacs=True,
        autoStaticArp=True
    )

    # Pastikan semua switch pakai OpenFlow10
    for sw in net.switches:
        sw.cmd('ovs-vsctl set Bridge {} protocols=OpenFlow10'.format(sw.name))

    net.start()

    h1, h2, h3, h4, h5 = net.get('h1', 'h2', 'h3', 'h4', 'h5')

    info("*** Ping dari h1 ke h2 dan h5\n")
    print(h1.cmd('ping -c 4 10.0.0.2'))  # h2
    print(h1.cmd('ping -c 4 10.0.0.5'))  # h5

    info("*** iperf dari h1 ke h2 dan ke h5\n")
    print(h2.cmd('iperf -s &'))
    print(h5.cmd('iperf -s &'))
    print(h1.cmd('iperf -c 10.0.0.2'))
    print(h1.cmd('iperf -c 10.0.0.5'))

    info("*** pingall\n")
    print(net.pingAll())

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
