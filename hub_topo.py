from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class SimpleHubTopo(Topo):
    def build(self):
        switch = self.addSwitch('s1')
        hosts = []
        for h in range(1, 6):
            host = self.addHost(f'h{h}')
            hosts.append(host)
            self.addLink(host, switch)

def run():
    topo = SimpleHubTopo()
    net = Mininet(topo=topo, controller=None)  # Controller eksternal (POX)
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
