'''
File: wolfmp.py
Author: Sigurd Fosseng
Description: UDP protocol for RTCW
'''

from utils.wolfutil import find_command
from utils.wolfutil import build_challenge
from twisted.internet.protocol import ClientFactory, ServerFactory, DatagramProtocol
from twisted.internet import reactor

class WolfProtocol(DatagramProtocol):
    def __init__(self):
        self.packet_prefix = '\xff' * 4

    def startListening(self):
        pass

    def stopProtocol(self):
        pass

    def startProtocol(self):
        pass

    def sendMessage(self, message, address):
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
            print "a package with the wrong prefix received"


    def message(self, command, *args):
        handler = getattr(self, 'handle_%s' % (command, ), None)

        if not handler:
            print "a handler for %s was not found" % (command, )
            return None

        try:
            return handler(*args)
        except:
            return None
