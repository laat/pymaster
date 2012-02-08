import sys, json
from twisted.internet import reactor
from twisted.web import server, resource
from twisted.web.static import File
from twisted.python import log
from datetime import datetime



class ServerList(resource.Resource):
    def __init__(self, servers):
        self.servers = servers

        self.children = {
                "ListServers": ListServers(servers)
        }

    def render_GET(self, request):
        return "Welcome to the server_list API"

    def getChild(self, name, request):
        if name == "":
            return self
        else:
            if name in self.children.keys():
                return resource.Resource.getChild(self, name, request)
            else:
                return NotFound(self)

class ListServers(resource.Resource):
    servers = {}

    def __init__(self, servers):
        self.servers = servers
        self.children = {}

    def render_GET(self, request):
        return json.dumps(self.servers)

class NotFound(resource.Resource):
    def __init__(self, node):
        self.node = node

    def render_GET(self, request):
        return "available resources is:<br> " + " ".join(self.node.children.keys())
        return "%s"%(self.node.children.keys())

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    log.msg("Starting server: %s"%(str(datetime.now())))

    servers = {"123.123.123.123: 3030": {1:1, 2:2}}
    root = ServerList(servers)

    server = server.Site(root)
    reactor.listenTCP(8080, server)
    reactor.run()
