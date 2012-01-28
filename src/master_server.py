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

class Servers(object):
    servers = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

    def _timeout(self, host, port):
        if time.time() - self.servers[host][port]["timestamp"] > 4:
            print time.time() - self.servers[host][port]["timestamp"]
            print "timeout %s:%s"%(host, port)
            self.remove_server(host, port)

    def update(self, infodict, host, port):
        """
        Updates information about this server
        returns the challenge if the server is new
        """
        new = False  # if this server is new, return new challenge key
        if not port in self.servers[host]: #NEW
            print "new"
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
        else:
            print "updated server"

        server = self.servers[host][port]
        server["timestamp"] = time.time()

        if infodict:  #  update the server with new infodict
            if "challenge" in infodict and server["challenge"] == infodict["challenge"]:  # spoofprotect
                server["infodict"].update(infodict)
            else:
                self.remove_server(host, port)

        print self.servers

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


class WolfMasterServerProtocol(WolfProtocol):
    def __init__(self):
        self.servers = Servers()
        self.packet_prefix = '\xff' * 4 # todo should inherit

    def _update(self, infodict, host, port):
        if infodict is None:
            infodict = {}

        new_server = self.servers.update(infodict, host, port)  # the challenge if new
        if new_server:
            getinfo_task = LoopingCall(self.getstatus, (host, port), challenge=new_server)
            self.servers.add_task(host, port, getinfo_task)
            getinfo_task.start(2)  # 5 minute intervall between getinfo

        return new_server

    def handle_heartbeat(self, content, host, port):
        print "heartbeat " + content
        self._update(None, host, port)

    def handle_gameCompletestatus(self, content, host, port):
        print "gameCompletestatus" + content
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

if __name__ == '__main__':
    from twisted.internet import reactor
    server = reactor.listenUDP(27950, WolfMasterServerProtocol())
    server.protocol._update(None,  "129.241.106.172", 27960)
    #server.protocol.getinfo(('213.239.214.164', 27961))  # HASDM
    #server.protocol.getinfo(('129.241.106.172', 27960))  # cky-beach info
    reactor.run()
