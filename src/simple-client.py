'''
File: simple-client.py
Author: Sigurd Fosseng
Description: A simple client for getting responses from servers
'''
from protocol.wolfmp import WolfProtocol

class WolfClientProtocol(WolfProtocol):
    def getinfo(self, address, challenge = ""):
        print "Sending getinfo %s to %s" % (challenge, address)
        self.sendMessage(" ".join(["getinfo", challenge]), address)

    def getstatus(self, address):
        self.sendMessage("getstatus", address)

    def handle_infoResponse(self, content, *args):
        print "infoResponse: " + content

    def handle_statusResponse(self, content, *args):
        print "statusResponse: "+ content


if __name__ == '__main__':
    from twisted.internet import reactor
    server = reactor.listenUDP(0, WolfClientProtocol())
    #server.protocol.getinfo(('213.239.214.164', 27961)) # HASDM
    #server.protocol.getinfo(('129.241.106.172', 27960))  # cky-beach info
    #server.protocol.getstatus(('213.239.214.164', 27961)) # HASDM
    server.protocol.getstatus(('93.186.192.128', 23352)) # CU'DM

    reactor.run()
