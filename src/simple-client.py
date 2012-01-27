'''
File: simple-client.py
Author: Sigurd Fosseng
Description: A simple client for getting responses from servers
'''
from protocol.wolfmp import WolfProtocol
from protocol.utils.wolfutil import infostring_to_dict

class WolfClientProtocol(WolfProtocol):
    def handle_infoResponse(self, content, *args):
        print content

    def handle_statusResponse(self, content, *args):
        print infostring_to_dict(content)

    def getstatus(self, address):
        self.sendMessage("getstatus", address)

if __name__ == '__main__':
    from twisted.internet import reactor
    server = reactor.listenUDP(0, WolfClientProtocol())
    server.protocol.getinfo(('213.239.214.164', 27961)) # HASDM
    server.protocol.getinfo(('129.241.106.172', 27960))  # cky-beach info
    server.protocol.getstatus(('213.239.214.164', 27961)) # HASDM


    reactor.run()
