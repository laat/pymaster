import json
from twisted.web import resource


class Root(resource.Resource):
    def __init__(self, servers):
        self.servers = servers
        resource.Resource.__init__(self)
        self.putChild("protocols", Protocols(servers))
        self.putChild("server", Server(servers))
        self.putChild("serverlist", ServerList(servers))

    def render_GET(self, request):
        return "/protocols <br> /serverlist/57 <br>"\
               " FUTURE FEATUE: /server/host/port"

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
        request.setHeader('Content-type', 'application/json')
        request.setHeader('Access-Control-Allow-Origin', '*')
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
            request.setHeader('Content-type', 'application/json')
            request.setHeader('Access-Control-Allow-Origin', '*')
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
        if len(request.postpath) != 2:
            return "server/10.0.0.1/27000 <br> server/ip/port"
        else:
            request.setHeader('Content-type', 'application/json')
            request.setHeader('Access-Control-Allow-Origin', '*')
            ip, port = request.postpath
            return json.dumps(self.servers.get_server_status(ip, port))
