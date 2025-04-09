from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class MacLearningSwitch(object):
    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {} # Dictionary to store MAC-to-port mapping
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        in_port = event.port
        src_mac = str(packet.src)
        dst_mac = str(packet.dst)

        # Learn the source MAC address and its port
        self.mac_to_port[src_mac] = in_port

        if dst_mac in self.mac_to_port:
            out_port = self.mac_to_port[dst_mac]
            # Install flow for future packets
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.actions.append(of.ofp_action_output(port=out_port))
            self.connection.send(msg)

            # Send the current packet
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=out_port))
            self.connection.send(msg)
        else:
            # Flood if the destination MAC is unknown
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            self.connection.send(msg)

def launch():
    def start_switch(event):
        log.debug(f"MacLearningSwitch connected to {event.connection}")
        MacLearningSwitch(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)