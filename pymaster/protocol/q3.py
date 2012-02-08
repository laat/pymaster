'''
File: wolfmp.py
Author: Sigurd Fosseng
Description: UDP protocol for Quake3
'''

from utils.q3util import find_command
from twisted.internet.protocol import DatagramProtocol
from twisted.python import log


class Q3Protocol(DatagramProtocol):
    """
    A simple implementation of the rtcw UDP-protocol.

    To handle commands sendt to this server, one must add methods with
    the prefix handle_ with the ending of the command
    """
    def __init__(self):
        self.packet_prefix = '\xff' * 4

    def sendMessage(self, message, address):
        """
        Sends a message witht the correct prefix
        """
        self.transport.write('%s%s\n'%(self.packet_prefix, message), address)

    def datagramReceived(self, data, (host, port)):
        if data.startswith(self.packet_prefix):
            #get the command from the package
            data = data.lstrip(self.packet_prefix)
            command, content = find_command(data)

            #get a response from package handler
            response = self.message(command, content, host, port)
            if response:
                self.sendMessage(response, (host, port))

        else:
            log.msg("a package with the wrong prefix received")

    def message(self, command, *args):
        """
        Routes incoming packages to the correct handler
        """
        handler = getattr(self, 'handle_%s' % (command, ), None)

        if not handler:
            log.msg("a handler for %s was not found" % (command, ))
            return None
        try:
            return handler(*args)
        except:
            return None
