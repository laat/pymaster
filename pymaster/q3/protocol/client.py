'''
File: clients.py
Author: Sigurd Fosseng
Description: Client protocols for Quake 3
'''
from .utils.q3util import unpack_host
from .utils.q3util import infostring_to_dict
from .utils.q3util import statusresponse_to_dict
from twisted.python import log
from .protocol import Q3Protocol


class ServerClientProtocol(Q3Protocol):
    """
    Client <-> Server protocol
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
        raise NotImplementedError

    def _update_status(self, statusdict, ip, port):
        raise NotImplementedError


class MasterServerClientProtocol(Q3Protocol):
    """
    Client <-> Master Server protocol
    """

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
        """
        Should return a tuple of (challenge_string, boolean)
        where the boolean indicates that it was created
        """
        raise NotImplementedError
