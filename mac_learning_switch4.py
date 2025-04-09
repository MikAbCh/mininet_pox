from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class MacLearningSwitch(object):
    def __init__(self, connection):
        # Simpan koneksi dan buat mapping MAC ke port
        self.connection = connection
        self.mac_table = {}  # format: {mac: port}
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        in_port = event.port

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        src_mac = packet.src
        dst_mac = packet.dst

        # Pelajari port asal dari MAC sumber
        self.mac_table[src_mac] = in_port

        if dst_mac in self.mac_table:
            out_port = self.mac_table[dst_mac]

            # Install flow untuk komunikasi langsung ke depan
            fm = of.ofp_flow_mod()
            fm.match = of.ofp_match.from_packet(packet, in_port)
            fm.actions.append(of.ofp_action_output(port=out_port))
            self.connection.send(fm)

            # Kirim paket ini juga secara langsung
            po = of.ofp_packet_out()
            po.data = event.ofp
            po.in_port = in_port
            po.actions.append(of.ofp_action_output(port=out_port))
            self.connection.send(po)
        else:
            # Flood jika belum tahu tujuan
            po = of.ofp_packet_out()
            po.data = event.ofp
            po.in_port = in_port
            po.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            self.connection.send(po)

def launch():
    def start_switch(event):
        log.info("Switch %s connected" % (event.connection.dpid,))
        MacLearningSwitch(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
