'''
File: motd_server.py
Author: Sigurd Fosseng
Description: A simple MOTD server that displays a given text string

RTCW motd port: 27951
'''
from protocol.utils.wolfutil import server_response_to_dict
from protocol.q3 import Q3Protocol


class Q3MotdServerProtocol(Q3Protocol):
    def handle_motd(self, content, host, port):
        content.strip("\"").lstrip("\"").lstrip("\\")
        infodict = server_response_to_dict(content)
        motd = "Hello World!"
        returnstring = "motd \"challenge\\%s\\%s\\\"" %\
                (infodict["challenge"], motd)

        self.sendMessage(returnstring, (host, port))

if __name__ == '__main__':
    from twisted.internet import reactor
    server = reactor.listenUDP(27951, Q3MotdServerProtocol())
