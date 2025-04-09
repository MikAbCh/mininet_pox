from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class MacLearningSwitch(object):
    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {}

        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        in_port = event.port
        src = packet.src
        dst = packet.dst

        self.mac_to_port[src] = in_port

        if dst in self.mac_to_port:
            out_port = self.mac_to_port[dst]
            log.info(f"[Switch {event.connection.dpid}] Kirim langsung ke port {out_port} untuk {dst}")

            # Pasang aturan flow untuk dst
            flow_mod = of.ofp_flow_mod()
            flow_mod.match = of.ofp_match.from_packet(packet, in_port)
            flow_mod.actions.append(of.ofp_action_output(port=out_port))
            self.connection.send(flow_mod)

            # Kirim langsung juga paket ini
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=out_port))
            msg.in_port = in_port
            self.connection.send(msg)

        else:
            log.info(f"[Switch {event.connection.dpid}] Flood untuk {dst}")
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            msg.in_port = in_port
            self.connection.send(msg)

def launch():
    def start_switch(event):
        log.info(f"Switch {event.connection.dpid} terkoneksi.")
        MacLearningSwitch(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
