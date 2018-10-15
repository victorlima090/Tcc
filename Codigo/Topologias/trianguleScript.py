#!/usr/bin/python
# -*- Coding: utf8 -*-
#coding: utf-8
"""Custom topology example


Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, UserSwitch 
from mininet.node import Controller, RemoteController, OVSController


class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."
        linkParameter = dict(bw=15,delay='0.5ms',loss=0.0001,max_queue_size=100000,use_htb=True)
        # Initialize topology
        Topo.__init__( self )
        # Add hosts and switches
        h1 = self.addHost( 'h1' , ip='10.0.0.1/32', mac='00:04:00:00:00:01' )
        h2 = self.addHost( 'h2' , ip='10.0.0.1/32', mac='00:04:00:00:00:01' )

        s1 = self.addSwitch( 's1' )

        # Add links
        self.addLink( h1, s1,**linkParameter)
        self.addLink(h2, s1 , **linkParameter)

def simpleTest():
    "Crete and teste a simple network"
    topo = MyTopo()
    net = Mininet(topo,controller = RemoteController, link = TCLink)
    net.addNAT().configDefault()
    net.start()
    #linkdown = net.configLinkStatus('s1','s3','down')
    #print linkdown
    dumpNodeConnections(net.hosts)
    CLI( net )
    net.stop()
if __name__ == '__main__':
	# Tell mininet to print useful information
	setLogLevel('info')
	simpleTest()

#topos = { 'mytopo':  MyTopo }
