'''
File: clients.py
Author: Sigurd Fosseng
Description: Client protocols for quake3
'''
from pymaster.q3.utils.q3util import unpack_host
from pymaster.q3.utils.q3util import infostring_to_dict
from pymaster.q3.utils.q3util import statusresponse_to_dict
from twisted.python import log
from protocol import Q3Protocol


class ServerClientProtocol(Q3Protocol):
    """
    Information queries sent to the game server
    """
    def getinfo(self, ip, port, challenge=""):
        log.msg("Sending getinfo to %s:%s" % (ip, port))
        self.sendMessage(" ".join(["getinfo", challenge]), (ip, port))

    def getstatus(self, ip, port, challenge=""):
        log.msg("Sending getstatus to %s:%s" % (ip, port))
        self.sendMessage(" ".join(["getstatus", challenge]), (ip, port))

    def handle_infoResponse(self, content, ip, port):
        log.msg("infoResponse from %s:%s" % (ip, port))
        infodict = infostring_to_dict(content)
        self._update_info(infodict, ip, port)

    def handle_statusResponse(self, content, ip, port):
        log.msg("statusResponse from %s:%s" % (ip, port))
        statusdict = statusresponse_to_dict(content)
        self._update_status(statusdict, ip, port)

    def _update_info(self, infodict, ip, port):
        pass

    def _update_status(self, statusdict, ip, port):
        pass

class MasterServerClientProtocol(Q3Protocol):
    """ Queries to the master server """

    def getservers(self, address, argumentlist):
        log.msg("Sending getservers with arguments %s to %s" %\
                (argumentlist, address))

        self.sendMessage("getservers " + " ".join(argumentlist), address)

    def handle_getserversResponse(self, content, ip, port):
        log.msg("getserversResponse from %s:%s" % (ip, port))
        content = content.strip("\\EOT\0\0\0")
        servers = content.split("\\")
        for s in servers:
            t = unpack_host(s)
            self._get_or_create_server(t[0], t[1])

    def get_or_create_server(self, ip, port):
        pass
