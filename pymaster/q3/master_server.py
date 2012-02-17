'''
File: master_server.py
Author: Sigurd Fosseng
Description: Master Server implementation
'''
from protocol.master_server import MasterServerProtocol
from protocol.client import MasterServerClientProtocol
from twisted.internet.task import LoopingCall
from random import randint
from abuse_filter import AbusiveClientFilter


class MasterServer(MasterServerProtocol,
        MasterServerClientProtocol):
    def __init__(self, servers):
        self.servers = servers
        self.abusive_filter = AbusiveClientFilter()
        MasterServerProtocol.__init__(self)
        MasterServerClientProtocol.__init__(self)

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
        from twisted.internet import reactor
        challenge, new = self.servers.get_or_create_server(ip, port)
        if new:  # start polling for info
            getinfo_task = LoopingCall(self.getinfo, ip, port,
                    challenge=challenge)
            self.servers.add_task(ip, port, getinfo_task)
            # not all at once.
            reactor.callLater(randint(1,40), getinfo_task.start, 300)

            getstatus_task = LoopingCall(self.getstatus, ip, port,
                    challenge=challenge)
            self.servers.add_task(ip, port, getstatus_task)
            reactor.callLater(randint(1,40), getstatus_task.start, 300)

        return challenge, new

    def _update_info(self, infodict, ip, port):
        self.servers.update(ip, port, infodict=infodict)

    def _update_status(self, statusdict, ip, port):
        self.servers.update(ip, port, statusdict=statusdict)

    def datagramReceived(self, data, (host, port)):
        if self.abusive_filter.filter_now(host):
            return  # filter this package

        MasterServerProtocol.datagramReceived(self, data, (host, port))
