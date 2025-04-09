from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class MacLearningSwitch(object):
    def __init__(self, connection):
        self.connection = connection
        self.mac_table = {}  # Format: {MAC: port}
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        in_port = event.port

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        src_mac = packet.src
        dst_mac = packet.dst

        # Simpan MAC sumber dan port asal
        self.mac_table[src_mac] = in_port

        if dst_mac in self.mac_table:
            out_port = self.mac_table[dst_mac]

            # Install flow supaya switch bisa handle sendiri ke depannya
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.actions.append(of.ofp_action_output(port=out_port))
            self.connection.send(msg)

            # Kirim langsung paket ini
            po = of.ofp_packet_out()
            po.data = event.ofp
            po.actions.append(of.ofp_action_output(port=out_port))
            po.in_port = in_port
            self.connection.send(po)
        else:
            # Flood jika belum tahu port tujuan
            po = of.ofp_packet_out()
            po.data = event.ofp
            po.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            po.in_port = in_port
            self.connection.send(po)

def launch():
    def start_switch(event):
        log.info(f"Switch {event.connection.dpid} connected")
        MacLearningSwitch(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
