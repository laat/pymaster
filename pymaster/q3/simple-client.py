'''
File: simple-client.py
Author: Sigurd Fosseng
Description: A simple client for getting responses from servers
'''
from protocol.q3 import Q3Protocol
from struct import unpack

class WolfClientProtocol(Q3Protocol):

    def getinfo(self, address, challenge = ""):
        print "Sending getinfo %s to %s" % (challenge, address)
        self.sendMessage(" ".join(["getinfo", challenge]), address)

    def getstatus(self, address):
        self.sendMessage("getstatus", address)

    def handle_infoResponse(self, content, *args):
        print "infoResponse: " + content

    def handle_statusResponse(self, content, *args):
        print "statusResponse: "+ content

    def getservers(self, address):
        print "getservers"+str(address)
        self.sendMessage("getservers 57 empty full", address)

    def handle_getserversResponse(self, content, *args):
        def get_pair(string):
            data = unpack(">BBBBH", string)
            host = "%d.%d.%d.%d"% data[:-1]
            port = data[-1]
            return host, port

        print "getserversResponse:"+content
        content = content.strip("\\EOT\0\0\0")
        servers = content.split("\\")
        for server in servers:
            print get_pair(server)


if __name__ == '__main__':
    from twisted.internet import reactor
    server = reactor.listenUDP(0, WolfClientProtocol())
    #server.protocol.getinfo(('213.239.214.164', 27961)) # HASDM
    #server.protocol.getinfo(('129.241.106.172', 27960))  # cky-beach info
    #server.protocol.getstatus(('213.239.214.164', 27961)) # HASDM
    #server.protocol.getstatus(('93.186.192.128', 23352)) # CU'DM
    server.protocol.getservers(('129.241.105.225', 27950)) # absint master
    #server.protocol.getservers(('64.22.107.125', 27950)) # wolfmaster.s4ndmod.com
    #server.protocol.getservers(("192.246.40.70", 27950))

    reactor.run()
