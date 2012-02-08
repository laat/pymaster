'''
File: master_server.py
Author: Sigurd Fosseng
Description: Master Server implementation

This implementation aims to cover all games that uses the quake 3
protocol
'''
from protocol.utils.q3util import infostring_to_dict
from protocol.utils.q3util import pack_host, unpack_host
from twisted.internet.task import LoopingCall
from twisted.python import log
from protocol.q3 import Q3Protocol
from server_list import Servers
import time, sys


flatlines = ["WolfFlatline-1", "ETFlatline-1"]

class Q3MasterServerProtocol(Q3Protocol):
    def __init__(self):
        self.servers = Servers()
        self.packet_prefix = '\xff' * 4 # todo should inherit

    def _update(self, infodict, host, port):
        if infodict is None:
            infodict = {}

        new_server = self.servers.update(infodict, host, port)  # the challenge if new
        if new_server:
            getinfo_task = LoopingCall(self.getinfo, (host, port), challenge=new_server)
            self.servers.add_task(host, port, getinfo_task)
            getinfo_task.start(300)  # 5 minute intervall between getinfo

        return new_server

    def handle_heartbeat(self, content, host, port):
        """
        This implementation ignores flatlines, and lets the servers time
        out instead. This is because the simplest implementation is
        vulnurable to spoofed packages and ... I'm lazy ;) However this
        works.
        TODO: Implement proper flatline handling
        """
        log.msg("heartbeat "+ content)
        if content in flatlines:
            return  # ignore
        self._update(None, host, port)
        self.getinfo(self, (host, port), challenge=self.servers.get(host, port)["challenge"])

    def getinfo(self, address, challenge = ""):
        log.msg("Sending getinfo %s to %s" % (challenge, address))
        self.sendMessage(" ".join(["getinfo", challenge]), address)

    def handle_gameCompleteStatus(self, content, host, port):
        log.msg("gameCompleteStatus" + content)
        self._update(None, host, port)

    def handle_infoResponse(self, content, host, port):
        log.msg("infoResponse from %s:%s"%(host, port))
        infodict = infostring_to_dict(content)
        self._update(infodict, host, port)

    def handle_getservers(self, content, host, port):
        """
        Sends sgetserverResponse messages to clients containing all servers
        TODO: respect filtering options
        """

        def split_it(servers, length):
            l = len(servers)
            i = 0
            while i+length<l:
                yield servers[i:i+length]
                i = i + length
            yield servers[i:]

        log.msg("getserver" + content)
        end = "\\EOT\0\0\0"
        delim = "\\"
        max_servers_in_package = 30  # 18*8+(7*8*30)+4*8 = 1856

        content = content.split(" ")
        # one of the first two is the protocol
        if content[0].isdigit():
            protocol = content[0]
            filter_strings = content[1:]
        elif content[1].isdigit():
            protocol = content[1]
            filter_strings = content[2:]
        else:
            return  # malformed package

        empty, full, gametype = False, False, False
        for f in filter_strings:
            if f == "empty":
                empty = True  # include empty
            elif f == "full":
                full = True  # inclure full

            #quake 3
            elif f == "ffa":
                gametype = "0"
            elif f == "tourney":
                gametype = "1"
            elif f == "team":
                gametype = "2"
            elif f == "ctf":
                gametype = "3"

            #darkplaces
            elif f.startswith("gametype="):
                gametype = f.lstrip("gametype=").strip("\n")


        servers = self.servers.get_servers(protocol, empty=empty, full=full, gametype=gametype)
        #construct packets
        for srvs in split_it(servers, max_servers_in_package):
            packed_srvs = [pack_host(s[0], s[1]) for s in srvs]
            self.sendMessage("getserversResponse\\"+delim.join(packed_srvs)+end,
                    (host, port))

    def getservers(self, address, argumentlist):
        log.msg("Sending getservers with arguments %s to %s" % (argumentlist, address))
        self.sendMessage("getservers "+ " ".join(argumentlist), address)

    def handle_getserversResponse(self, content, *args):
        log.msg("getserversResponse:")
        content = content.strip("\\EOT\0\0\0")
        servers = content.split("\\")
        for s in servers:
            t = unpack_host(s)
            self._update(None, t[0], t[1])


if __name__ == '__main__':
    from twisted.internet import reactor
    log.startLogging(sys.stdout)
    server = reactor.listenUDP(27950, Q3MasterServerProtocol())
    #server.protocol._update(None,  "129.241.106.172", 27960)  # cky-beach
    #server.protocol.getservers(('129.241.105.225', 27950), ["57","empty", "full"]) # absint master
    server.protocol.getservers(('64.22.107.125', 27950), ["57","empty", "full"]) # wolfmaster.s4ndmod.com
    #server.protocol.getinfo(('213.239.214.164', 27961))  # HASDM
    #server.protocol.getinfo(('129.241.106.172', 27960))  # cky-beach info
    reactor.run()
