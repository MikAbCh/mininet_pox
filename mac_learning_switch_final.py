from pox.core import core
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.openflow.libopenflow_01 import *

log = core.getLogger()

class LearningSwitch(object):
    def __init__(self, connection):
        self.connection = connection
        self.macToPort = {}
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        in_port = event.port

        self.macToPort[packet.src] = in_port

        if packet.dst in self.macToPort:
            out_port = self.macToPort[packet.dst]

            # Pasang flow rule untuk lalu lintas ke depan
            msg = ofp_flow_mod()
            msg.match = ofp_match.from_packet(packet, in_port)
            msg.actions.append(ofp_action_output(port=out_port))
            msg.idle_timeout = 60
            self.connection.send(msg)

            self._send_packet(packet, out_port, event)
        else:
            self._send_packet(packet, OFPP_ALL, event)

    def _send_packet(self, packet, port, event):
        msg = ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(ofp_action_output(port=port))
        msg.in_port = event.port
        self.connection.send(msg)

def launch():
    def start_switch(event):
        log.info("Switch %s connected" % dpidToStr(event.dpid))
        LearningSwitch(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
