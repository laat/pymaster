'''
File: server_list.py
Author: Sigur Fosseng
Description: A server list implementation
'''
from protocol.utils.wolfutil import build_challenge
from twisted.internet.task import LoopingCall
from collections import defaultdict
import time


class ProtocolIndex(object):
    """
    A class for quick lookups when replying to getservers
    """
    protocol_index = defaultdict(set)  #for quick lookups

    def add_server(self, protocol, host, port):
        self.protocol_index[protocol].add((host, port))

    def remove_server(self, host, port):
        for protocol, servers in self.protocol_index.iteritems():
            if (host, port) in servers:
                servers.remove((host, port))

    def get_servers(self, protocol):
        return list(self.protocol_index[protocol])

class Servers(object):
    """
    This object is in control of all the information about servers
    """
    servers = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

    def __init__(self):
        self.protocol_index = ProtocolIndex()

    def _timeout(self, host, port):
        """
        The method is called when the server has not been heared from
        the last 400 secounds
        """
        if time.time() - self.servers[host][port]["timestamp"] > 400:
            self.remove_server(host, port)
            self.protocol_index.remove_server(host, port)
            print "timeout %s:%s"%(host, port)

    def _new_server(self, host, port):
        """ initialises a new server instance """
        #self.servers[host][port]["state"] = SV_STATE["unknown"]
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
                del infodict["challenge"] # this is not needed any more
                server["infodict"].update(infodict)
                server["empty"] = infodict["clients"] == "0"
                server["full"] = infodict["sv_maxclients"] == infodict["clients"]
            else:
                self.remove_server(host, port)

            # add the server to the protocol index
            if "protocol" in infodict:
                self.protocol_index.add_server(infodict["protocol"], host, port)

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

    def get_servers(self, protocol, empty=True, full=True, gametype=None):
        all_servers = self.protocol_index.get_servers(protocol)
        if empty and full and not gametype:
            return all_servers
        else:  #do some filtering
            srvs = []
            for host, port in all_servers:
                s = self.servers[host][port]

                filter_this = False
                if not full and s["full"]: # Do not want full servers -> filter
                    filter_this = True
                if not empty and s["empty"]:
                    filter_this = True
                if gametype and gametype != s["infodict"]["gametype"]:
                    filter_this = True

                if not filter_this:
                    srvs.append((host, port))
                else:
                    pass  #print "filtered %s:%s"%(host, port)

            return srvs
