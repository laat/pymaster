from twisted.application import service, internet
from twisted.internet import endpoints, protocol
from twisted.python import log
from twisted.python import usage
from pymaster.q3.master_server import Q3MasterServerProtocol

Q3MASTER_PORT = "27950"

class Options(usage.Options):
    optFlags = [
        ['debug', 'd', 'Emit debug messages']
    ]
    optParameters = [
        ["q3master_port", "p", Q3MASTER_PORT,
            "port the q3 master server runs on"]
    ]

class MasterServerService(service.Service):
    name = "Q3 Master Service"

    def __init__(self, port):
        self.port = port

    def startService(self):
        from twisted.internet import reactor
        log.msg("starting server")
        self.server = reactor.listenUDP(self.port, Q3MasterServerProtocol())
        self.server.protocol.getservers(('64.22.107.125', 27950), ["57","empty", "full"]) # wolfmaster.s4ndmod.com

def makeService(options):
    ms = service.MultiService()

    q3_master = MasterServerService(int(options["q3master_port"]))
    q3_master.setServiceParent(ms)

    return ms
