from pox.core import core
from pox.lib.util import dpid_to_str

log = core.getLogger()

class MyComponent(object):
    def __init__ (self):
        core.openflow.addListeners(self)
        log.debug("Hi starting the controller")
    def _handle_ConnectionUp (self, event):
        log.debug("Switch %s has come up", dpid_to_str(event.dpid))
    def _handle_ConnectionDown(self, event):
        log.debug("Swtich %s is down", dpid_to_str(event.dpid))

def launch():
    core.registerNew(MyComponent)