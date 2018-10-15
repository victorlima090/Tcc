"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, UserSwitch 
from mininet.node import Controller, RemoteController, OVSController


class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        middleHost = self.addHost('h3')
        nat = self.addNAT().configDefault()

        leftSwitch = self.addSwitch( 's1',cls=OVSKernelSwitch )
        rightSwitch = self.addSwitch( 's2',cls=OVSKernelSwitch )
        middleSwitch = self.addSwitch( 's3' ,cls=OVSKernelSwitch)

        # Add links
        self.addLink( leftHost, leftSwitch )
        self.addLink( rightHost , rightSwitch)
        self.addLink( middleHost , middleSwitch )

        self.addLink( leftSwitch, middleSwitch ) 
        self.addLink( leftSwitch, rightSwitch )
        self.addLink( middleSwitch, rightSwitch  )
        #self.addNAT().configDefault()


topos = { 'mytopo':  MyTopo }
