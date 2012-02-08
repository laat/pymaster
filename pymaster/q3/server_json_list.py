import sys
import json
from twisted.internet import reactor
from twisted.web import resource
from twisted.web import server
from twisted.python import log
from datetime import datetime


class Root(resource.Resource):
    def __init__(self, servers):
        self.servers = servers
        resource.Resource.__init__(self)
        self.putChild("protocols", Protocols(servers))
        self.putChild("server", Server(servers))
        self.putChild("serverlist", ServerList(servers))

    def render_GET(self, request):
        return "/protocols <br> /serverlist/57 <br> FUTURE FEATUE: /server/host/port"

    def getChild(self, path, request):
        if path == "":
            return self
        if path in self.children.keys():
            return resource.Resource.get(self, path, request)


class Protocols(resource.Resource):
    """
    GET: should return all protocols tracked by this server
    """
    isLeaf = True

    def __init__(self, servers):
        self.servers = servers
        resource.Resource.__init__(self)

    def render_GET(self, request):
        return json.dumps(self.servers.get_protocols())


class ServerList(resource.Resource):
    """
    GET: should return all server and their information
    """
    isLeaf = True

    def __init__(self, servers):
        self.servers = servers
        resource.Resource.__init__(self)

    def render_GET(self, request):
        if request.postpath == []:
            return "/serverlist/57 <br> the 57 means the protocol number "
        else:
            protocol = request.postpath[0]
            return json.dumps(self.servers.get_servers_info(protocol))


class Server(resource.Resource):
    """
    GET: should return the status of this server
    """
    isLeaf = True

    def __init__(self, servers):
        self.servers = servers
        resource.Resource.__init__(self)

    def render_GET(self, request):
        return "to be implemented"

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    log.msg("Starting server: %s" % (str(datetime.now())))
    root = Root()
    server = server.Site(root)
    reactor.listenTCP(8080, server)

    reactor.run()
