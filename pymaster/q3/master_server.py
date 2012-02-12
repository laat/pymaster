'''
File: master_server.py
Author: Sigurd Fosseng
Description: Master Server implementation
'''
from protocol.master_server import MasterServerProtocol
from protocol.client import MasterServerClientProtocol
from twisted.internet.task import LoopingCall
from twisted.python import log
from random import randint
import sys



class MasterServer(MasterServerProtocol,
        MasterServerClientProtocol):
    def __init__(self, servers):
        self.servers = servers
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
