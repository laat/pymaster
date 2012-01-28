'''
File: servers.py
Author: Sigurd Fosseng
Description: internal serverlist
'''
from protocol.utils.wolfutil import build_challenge
from protocol.utils.wolfutil import server_response_to_dict
from protocol.wolfmp import WolfProtocol
from twisted.internet.task import LoopingCall
from collections import defaultdict
from struct import unpack
import time


flatlines = ["WolfFlatline-1", "ETFlatline-1"]


SV_STATE = {
        "unknown": -1,
        "unused_slots" : 0,
        "uninitalized" : 1,
        "empty": 2,
        "occupied": 3,
        "full": 4
        }

class ProtocolIndex(object):
    """
    a class for quick lookups when replying to getservers
    """
    protocol_index = defaultdict(set)  #for quick lookups

    def add_server(self, protocol, host, port):
        self.protocol_index[protocol].add((host, port))
        print self.protocol_index

    def remove_server(self, host, port):
        for protocol, servers in self.protocol_index:
            if (host, port) in servers:
                servers.remove((host, port))

    def get_servers(self, protocol):
        return list(self.protocol_index[protocol])

class Servers(object):
    servers = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

    def __init__(self):
        self.protocol_index = ProtocolIndex()

    def _timeout(self, host, port):
        if time.time() - self.servers[host][port]["timestamp"] > 4:
            self.remove_server(host, port)
            self.protocol_index.remove_server(host, port)
            print time.time() - self.servers[host][port]["timestamp"]
            print "timeout %s:%s"%(host, port)

    def _new_server(self, host, port):
        #init server
        self.servers[host][port]["state"] = SV_STATE["unknown"]
        challenge = build_challenge()  # randomized challenge
        self.servers[host][port]["challenge"] = challenge

        # remove the server after a timeout
        timeout_task = LoopingCall(self._timeout, host, port)
        timeout_task.start(200, now=False)
        self.servers[host][port]["tasks"] = [timeout_task]

        new = challenge
        print "added a new server: %s:%s"%(host, port)
        return new


    def update(self, infodict, host, port):
        """
        Updates information about this server
        returns the challenge if the server is new
        """
        new = False  # if this server is new, return new challenge key
        if not port in self.servers[host]: #NEW
            new = self._new_server(host, port)

        # add timestamp
        server = self.servers[host][port]
        server["timestamp"] = time.time()

        #  update the server with new infodict
        if infodict:
            if "challenge" in infodict and server["challenge"] == infodict["challenge"]:  # spoofprotect
                server["infodict"].update(infodict)
            else:
                self.remove_server(host, port)

            # add the server to the protocol index
            if "protocol" in infodict:
                self.protocol_index.add_server(infodict["protocol"], host, port)

        print self.servers # Debug
        return new

    def remove_server(self, host, port):
        self.stop_tasks(host, port)
        del self.servers[host][port]

    def add_task(self, host, port, task):
        """
        tasks connected to this server
        """
        server = self.servers[host][port]
        server["tasks"].append(task)

    def stop_tasks(self, host, port):
        """
        stop all tasks associated with this server
        """
        server = self.servers[host][port]
        try:
            for t in server["tasks"]:
                t.stop()
        except:
            pass

    def get(self, host, port):
        return self.servers[host][port]

    def get_servers(self, protocol):
        return self.protocol_index.get_servers(protocol)

class WolfMasterServerProtocol(WolfProtocol):
    def __init__(self):
        self.servers = Servers()
        self.packet_prefix = '\xff' * 4 # todo should inherit

    def _update(self, infodict, host, port):
        print "update"
        if infodict is None:
            infodict = {}

        new_server = self.servers.update(infodict, host, port)  # the challenge if new
        if new_server:
            getinfo_task = LoopingCall(self.getstatus, (host, port), challenge=new_server)
            self.servers.add_task(host, port, getinfo_task)
            getinfo_task.start(30)  # 5 minute intervall between getinfo

        return new_server

    def handle_heartbeat(self, content, host, port):
        """
        This implementation ignores flatlines, and lets the servers time
        out instead. This is because the simplest implementation is
        vulnurable to spoofed packages and ... I'm lazy ;) However this
        works.
        TODO: Implement proper flatline handling
        """
        print "heartbeat " + content
        if content in flatlines:
            return  # ignore
        self._update(None, host, port)

    def handle_gameCompleteStatus(self, content, host, port):
        print "gameCompleteStatus" + content
        self._update(None, host, port)

    def getinfo(self, address, challenge = ""):
        print "Sending getinfo %s to %s" % (challenge, address)
        self.sendMessage(" ".join(["getinfo", challenge]), address)

    def handle_infoResponse(self, content, host, port):
        print "infoResponse from %s:%s"%(host, port)
        infodict = server_response_to_dict(content)
        self._update(infodict, host, port)

    def getstatus(self, address, challenge = ""):
        print "Sending getinfo %s to %s" % (challenge, address)
        self.sendMessage(" ".join(["getstatus", challenge]), address)

    def handle_statusResponse(self, content, host, port):
        print "statusResponse from %s:%s"%(host, port)
        infodict = server_response_to_dict(content, statusResponse=True)
        self._update(infodict, host, port)

    def handle_getserveres(self, content, host, port):
        print "getserver" + content
        # return a serverlist that is able to be sendt
        pass

    def getservers(self, address, argumentlist):
        self.sendMessage("getservers "+ " ".join(argumentlist), address)

    def handle_getserversResponse(self, content, *args):
        def get_pair(string):
            data = unpack(">BBBBH", string)
            host = "%d.%d.%d.%d"% data[:-1]
            port = data[-1]
            return host, port

        print "getserversResponse:"+content
        content = content.strip("\\EOT\0\0\0")
        servers = content.split("\\")
        print servers
        try:
            for s in servers:
                print s
                print get_pair(s)
                t = get_pair(s)
                self._update(None, t[0], t[1])
        except:
            import sys
            print sys.exc_info()

if __name__ == '__main__':
    from twisted.internet import reactor
    server = reactor.listenUDP(27950, WolfMasterServerProtocol())
    server.protocol._update(None,  "129.241.106.172", 27960)  # cky-beach
    server.protocol.getservers(('64.22.107.125', 27950), ["57","empty", "full"]) # wolfmaster.s4ndmod.com
    #server.protocol.getinfo(('213.239.214.164', 27961))  # HASDM
    #server.protocol.getinfo(('129.241.106.172', 27960))  # cky-beach info
    reactor.run()
