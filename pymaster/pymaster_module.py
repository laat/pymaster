from twisted.application import service, internet
from twisted.internet import endpoints, protocol
from twisted.python import log
from twisted.python import usage


class Options(usage.Options):
    optFlags = [['debug', 'd', 'Emit debug messages']]
    optParameters = [["endpoint", "s", DEFAULT_STRPORT,
                      "string endpoint descriptiont to listen on, defaults to 'tcp:80'"]]


class SetupService(service.Service):
    pass

