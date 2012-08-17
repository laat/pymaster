from twisted.application import service
from twisted.application import internet
from twisted.python import log
from twisted.python import usage
from twisted.web import server
from pymaster.q3.master_server import MasterServer
from pymaster.q3.server_list import Servers
from pymaster.q3.server_json_list import Root
import yaml

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
        ["master_server_file", "f", "master_servers.yaml",
            "the config file for masterservers"]
    ]


class MasterServerService(service.Service):
    name = "Q3 Master"

    def __init__(self, port, server_list, master_servers_file):
        self.port = port
        self.server_list = Servers()
        self.server = None
        self.master_servers_file = master_servers_file

    def startService(self):
        from twisted.internet import reactor
        log.msg("Starting %s Server on port %s" % (self.name, self.port))
        master_server = MasterServer(self.server_list)

        self.server = reactor.listenUDP(self.port, master_server)

        with file(self.master_servers_file) as f:
            master_servers = yaml.load(f.read())

        delay = 0
        for k, v in master_servers.items():
            for i in v:
                reactor.callLater(delay, self.server.protocol.loop_getservers,
                        (k, 27950), [str(i), "empty", "full"], 1800)
                delay = delay + 15


def makeService(options):
    server_list = Servers()
    ms = service.MultiService()

    q3_master = MasterServerService(int(options["q3master_port"]), server_list,
            options["master_server_file"])
    q3_master.setServiceParent(ms)

    json_root = server.Site(Root(server_list))
    json_api = internet.TCPServer(int(options["json_api_port"]), json_root)
    json_api.setServiceParent(ms)

    return ms
