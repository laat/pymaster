'''
File: server_list.py
Author: Sigur Fosseng
Description: A server list implementation
'''
from .protocol.utils.q3util import build_challenge
from twisted.internet.task import LoopingCall
from twisted.python import log
from collections import defaultdict
import time


class ProtocolIndex(object):
    """
    A class for quick lookups when replying to getservers
    """
    protocol_index = defaultdict(set)  # for quick lookups

    def add_server(self, protocol, host, port):
        self.protocol_index[protocol].add((host, port))

    def remove_server(self, host, port):
        for _, servers in self.protocol_index.iteritems():
            if (host, port) in servers:
                servers.remove((host, port))

    def get_servers(self, protocol):
        return list(self.protocol_index[protocol])

    def get_protocols(self):
        return self.protocol_index.keys()


class Servers(object):
    """
    This object is in control of all the information about servers
    """
    servers = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    def __init__(self):
        self.protocol_index = ProtocolIndex()

    def bump_time(self, host, port):
        """ bumps the time stamp, so we do not time out """
        self.servers[(host, port)]["timestamp"] = time.time()

    def get_or_create_server(self, host, port):
        """
        Creates new servers if not in list
        returns the challenge to the server
        """
        new = not (host, port) in self.servers  # server is new
        if new:
            challenge = self._new_server(host, port)
        else:
            challenge = self.servers[(host, port)]["challenge"]

        return challenge, new

    def _new_server(self, host, port):
        """
        initialises a new server instance
        returns the challenge
        """
        challenge = build_challenge()  # randomized challenge
        self.bump_time(host, port)
        self.servers[(host, port)]["challenge"] = challenge

        # remove the server after a timeout
        timeout_task = LoopingCall(self._timeout, host, port)
        timeout_task.start(200, now=False)
        self.servers[host, port]["tasks"] = [timeout_task]

        log.msg("added a new server: %s:%s" % (host, port))

        return challenge

    def update(self, host, port, infodict=None, statusdict=None):
        """
        Updates information about this server
        returns the challenge if the server is new
        """
        self.get_or_create_server(host, port)  # create the server if unknown

        server = self.servers[(host, port)]
        self.bump_time(host, port)

        challenge_match = False
        if infodict:
            challenge_match = "challenge" in infodict and\
                server["challenge"] == infodict["challenge"]
        if statusdict:
            challenge_match = "challenge" in statusdict and\
                server["challenge"] == statusdict["challenge"]

        #  update the server with new info
        if infodict and challenge_match:
            del infodict["challenge"]  # this is not needed any more
            server["infodict"].update(infodict)

                #calculate now for filtering later
            server["empty"] = infodict["clients"] == "0"
            server["full"] = infodict["sv_maxclients"] == infodict["clients"]

                # add the server to the protocol index
            if "protocol" in infodict:
                self.protocol_index.add_server(infodict["protocol"],
                            host, port)
            else:
                log.msg("SPOOF!: challenge from %s:%s did not match local" %
                        (host, port))

        if statusdict and challenge_match:
            del statusdict["challenge"]  # not needed
            server["statusdict"].update(statusdict)
            if "sv_privateClients" in statusdict:
                server["infodict"]["sv_privateClients"] = \
                        statusdict["sv_privateClients"]

        return

    def remove_server(self, host, port):
        self.protocol_index.remove_server(host, port)
        self.stop_tasks(host, port)
        del self.servers[(host, port)]

    def add_task(self, host, port, task):
        """
        tasks connected to this server
        """
        server = self.servers[(host, port)]
        server["tasks"].append(task)

    def stop_tasks(self, host, port):
        """
        stop all tasks associated with this server
        """
        server = self.servers[(host, port)]
        for t in server["tasks"]:
            try:
                t.stop()
            except:
                pass


    def get_servers(self, protocol, empty=True, full=True, gametype=None):
        all_servers = self.protocol_index.get_servers(protocol)
        if empty and full and not gametype:
            return all_servers
        else:  # do some filtering
            srvs = []
            for host, port in all_servers:
                s = self.servers[(host, port)]

                filter_this = False
                if not full and s["full"]:  # Do not want full servers -> filter
                    filter_this = True
                if not empty and s["empty"]:
                    filter_this = True
                if gametype and gametype != s["infodict"]["gametype"]:
                    filter_this = True

                if not filter_this:
                    srvs.append((host, port))
                else:
                    pass  # print "filtered %s:%s"%(host, port)

            return srvs

    def _timeout(self, host, port):
        """
        The method is called when the server has not been heared from
        the last 400 secounds
        """
        if time.time() - self.servers[(host, port)]["timestamp"] > 400:
            self.remove_server(host, port)
            log.msg("timeout %s:%s" % (host, port))

    def get(self, host, port):
        return self.servers[(host, port)]

    def get_protocols(self):
        return self.protocol_index.get_protocols()

    def get_servers_info(self, protocol):
        all_servers = self.protocol_index.get_servers(protocol)
        servers = []
        for host, port in all_servers:
            tmp = {"_host_port": "%s:%s" % (host, port), }
            tmp.update(self.servers[(host, port)]["infodict"])
            servers.append(tmp)
        return servers

    def get_server_status(self, host, port):
        port = int(port)
        return self.servers[(host, port)]["statusdict"]
