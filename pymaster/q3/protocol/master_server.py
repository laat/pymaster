'''
File: master_servers.py
Author: Sigurd Fosseng
Description: Master server protocols for Quake 3
'''
from .utils.q3util import pack_host
from .client import ServerClientProtocol
from twisted.python import log


class HeartBeatServerProtocol(ServerClientProtocol):
    """
    Server -> Master Server protocol
    """
    flatlines = [
            "WolfFlatline-1",  # RTCW
            "ETFlatline-1",  # ET
            "flatline",  # CoD 4! =)
        ]

    def handle_heartbeat(self, content, ip, port):
        """
        Handles heart messages received by the server.
        In reply to a heartbeat message it sends a getinfo message.
        """
        log.msg("heartbeat from %s:%s" % (ip, port))

        if content in self.flatlines:
            return  # ignore, could be spoofed

        challenge, _ = self._get_or_create_server(ip, port)
        self.getinfo(ip, port, challenge=challenge)

    def handle_gameCompleteStatus(self, content, ip, port):
        """
        Handles gameCompleteStatus messages.
        This method only calls _get_or_create_server. This is because
        this message from the game server is useless with the getinfo
        calls when the master server receives a heartbeat message.
        """
        log.msg("gameCompleteStatus" + content)

        # Notify server list that something happened
        # Used for timeout
        self._get_or_create_server(ip, port)

    def _get_or_create_server(self, ip, port):
        """
        Should return a tuple of (challenge_string, boolean)
        where the boolean indicates that it was created
        """
        raise NotImplementedError


class MasterServerProtocol(HeartBeatServerProtocol):
    def handle_getservers(self, content, host, port):
        """
        Sends getserverResponse messages to the sender.
        The server responds with a series of getserverResponse messages
        that contain all servers
        """
        log.msg("getserver" + content)
        end = "\\EOT\0\0\0"
        delim = "\\"
        max_servers_in_package = 30  # 18*8+(7*8*30)+4*8 = 1856

        protocol, filter_strings, _ = self._parse_package(content)
        empty, full, gametype = self._parse_filter(filter_strings)

        servers = self._get_servers(protocol, empty=empty,
                full=full, gametype=gametype)

        #construct and send packets
        for srvs in self._split_it(servers, max_servers_in_package):
            packed_srvs = [pack_host(s[0], s[1]) for s in srvs]
            self.sendMessage("getserversResponse\\" +
                    delim.join(packed_srvs) + end, (host, port))

    @classmethod
    def _parse_package(cls, content):
        """ extract protocol info and filter_strings """
        content = content.split(" ")
        protocol, filter_strings = None, None
        name = None  # darkplaces

        # one of the first two is the protocol
        if content[0].isdigit():
            protocol = content[0]
            filter_strings = content[1:]

        elif content[1].isdigit():
            # darkplaces
            name = content[0]
            protocol = content[1]
            filter_strings = content[2:]

        return protocol, filter_strings, name

    @classmethod
    def _parse_filter(cls, filter_strings):
        empty, full, gametype = False, False, False

        for f in filter_strings:
            if f == "empty":
                empty = True  # include empty
            elif f == "full":
                full = True  # include full

            # quake 3
            elif f == "ffa":
                gametype = "0"
            elif f == "tourney":
                gametype = "1"
            elif f == "team":
                gametype = "2"
            elif f == "ctf":
                gametype = "3"

            # darkplaces
            elif f.startswith("gametype="):
                gametype = f.lstrip("gametype=").strip("\n")

        return empty, full, gametype

    @classmethod
    def _split_it(cls, servers, length):
        """
        a generator that returns list chunks of the defined length
        """
        l = len(servers)
        i = 0
        while i + length < l:
            yield servers[i:i + length]
            i = i + length
        yield servers[i:]

    def _get_servers(self, protocol, empty=True, full=True, gametype=5):
        """
        Should return a list of (host, ip) tuples
        """
        raise NotImplementedError
