# -*- Coding: utf8 -*-
#coding: utf-8
from pox.core import core
from pox.lib.util import dpid_to_str
import pox.lib.packet as pkt
import featureExtraction2
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr
from collections import namedtuple
import capture
import struct
from collections import deque
import os
import dpkt

log = core.getLogger()

class captureModule(EventMixin):
    def __init__ (self):
        core.openflow.addListeners(self)
        log.debug("Hi starting the controller")

    def _handle_ConnectionUp (self, event):
        log.debug("Switch %s has come up", dpid_to_str(event.dpid))

    def _handle_ConnectionDown(self, event):
        log.debug("Swtich %s is down", dpid_to_str(event.dpid))

    def _handle_PacketIn (self, event):
        log.debug("PACKET IN ROLOU AKI")
        packet = event.parsed
        window_packet = deque()
        file = open("Results.txt","a")

        if packet is not None:
            packet_ip = packet.find('ipv4')
            if packet_ip is not None:
                print " IP PACKET "
                tcp_packet = packet_ip.find('tcp')
                if tcp_packet is not None:
                    print " TCP PACKET "
                    packet = packet.raw
                    header_pkt1 = packet_ip.hdr(packet_ip.payload) #header do pacote ipv4
                    header_pkt = struct.unpack('!BBHHHBBHII',header_pkt1) #retira ele da formatação
                    header = header_pkt[4]# pega o timestamp
                    window_packet.append((header,packet)) 
                    pred,actual = capture.process_packet(window_packet)
                    print ("Pred = %s \n Actual = %s" % (pred,actual))
                    if( pred == actual):
                        file.write("%s %s \n"%(pred,actual))
                    else:
                        file.write("%s %s 3\n"%(pred,actual))
                else:
                    print " UDP PACKET "
            else:
                print "not ip packet"
        else:
            print  " PACKET NOT PARSED"

def launch():
    core.registerNew(captureModule)