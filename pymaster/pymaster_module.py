from twisted.application import service
from twisted.application import internet
from twisted.python import log
from twisted.python import usage
from twisted.web import server
from pymaster.q3.master_server import Q3MasterServerProtocol
from pymaster.q3.server_list import Servers
from pymaster.q3.server_json_list import Root

Q3MASTER_PORT = "27950"
JSON_PORT = "8080"


class Options(usage.Options):
    optFlags = [
        ['debug', 'd', 'Emit debug messages']
    ]
    optParameters = [
        ["q3master_port", "p", Q3MASTER_PORT,
            "port the q3 master server runs on"],
        ["json_api_port", "q", JSON_PORT,
            "port the json api is served on"],
    ]


class MasterServerService(service.Service):
    name = "Q3 Master"

    def __init__(self, port):
        self.port = port
        self.server_list = Servers()

    def startService(self):
        from twisted.internet import reactor
        log.msg("Starting %s Server on port %s" % (self.name, self.port))
        master_server = Q3MasterServerProtocol(self.server_list)

        self.server = reactor.listenUDP(self.port, master_server)

        # wolfmaster.s4ndmod.com steal
        from twisted.internet import reactor
        reactor.callLater(5, self.server.protocol.getservers,
                ('64.22.107.125', 27950), ["57", "empty", "full"])
        reactor.callLater(10, self.server.protocol.getservers,
                ('64.22.107.125', 27950), ["60", "empty", "full"])
        reactor.callLater(15, self.server.protocol.getservers,
                ('64.22.107.125', 27950), ["68", "empty", "full"])
        reactor.callLater(20, self.server.protocol.getservers,
                ('64.22.107.125', 27950), ["71", "empty", "full"])


def makeService(options):
    ms = service.MultiService()

    q3_master = MasterServerService(int(options["q3master_port"]))
    q3_master.setServiceParent(ms)

    json_root = server.Site(Root(q3_master.server_list))
    json_api = internet.TCPServer(int(options["json_api_port"]), json_root)
    json_api.setServiceParent(ms)

    return ms
