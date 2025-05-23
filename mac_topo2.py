from mininet.topo import Topo

class L2LearningTopo(Topo):
    def build(self):
        # Tambah switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Tambah host
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')

        # Hubungkan host dengan switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)

        # Hubungkan antar switch
        self.addLink(s1, s2)
        self.addLink(s2, s3)

        # Hubungkan host ke switch s3
        self.addLink(h3, s3)
        self.addLink(h4, s3)
        self.addLink(h5, s3)

topos = {'l2topo': (lambda: L2LearningTopo())}
