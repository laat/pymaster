'''
File: master_server.py
Author: Sigurd Fosseng
Description: Master Server implementation
'''
from protocol.master_server import SnoopingMasterServerProtocol
from twisted.internet.task import LoopingCall
from twisted.python import log
from random import randint
import sys


class MasterServer(SnoopingMasterServerProtocol):
    def __init__(self, servers):
        self.servers = servers
        SnoopingMasterServerProtocol.__init__(self)

    def loop_getservers(self, address, argumentlist, delay):
        from twisted.internet import reactor
        loop = LoopingCall(self.getservers, address, argumentlist)

        #not all at once please
        reactor.callLater(randint(5, 30), loop.start, delay)

    def _get_servers(self, protocol, empty=True, full=True, gametype=None):
        """ returns a list of (host, port) tuples """
        return self.servers.get_servers(protocol, empty=empty, full=full,
                gametype=gametype)

    get_servers = _get_servers  # expose this

    def _get_or_create_server(self, ip, port):
        challenge, new = self.servers.get_or_create_server(ip, port)
        if new:  # start polling for info
            getinfo_task = LoopingCall(self.getinfo, ip, port,
                    challenge=challenge)
            self.servers.add_task(ip, port, getinfo_task)
            getinfo_task.start(300) # 5 minute intervall between getinfo

            getstatus_task = LoopingCall(self.getstatus, ip, port,
                    challenge=challenge)
            self.servers.add_task(ip, port, getstatus_task)
            getstatus_task.start(300) # 5 minute intervall between getstatus

        return challenge, new

    def _update_info(self, infodict, ip, port):
        self.servers.update(ip, port, infodict=infodict)

    def _update_status(self, statusdict, ip, port):
        self.servers.update(ip, port, statusdict=statusdict)

if __name__ == '__main__':
    from twisted.internet import reactor
    from server_list import Servers
    server_list = Servers()
    log.startLogging(sys.stdout)
    ms = MasterServer(server_list)
    server = reactor.listenUDP(27950, ms)
    print dir(server.protocol)
    server.protocol.getinfo("188.40.127.132", 27886)  # beach
    server.protocol.getservers(('64.22.107.125', 27950),
            ["57", "empty", "full"])  # wolfmaster.s4ndmod.com
    #server.protocol._update(None,  "129.241.106.172", 27960)  # cky-beach
    reactor.run()
