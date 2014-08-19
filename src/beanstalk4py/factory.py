#

from twisted.internet.protocol import ClientFactory

from protocol import BeanstalkClient


class BeanstalkClientFactory(ClientFactory):
    protocol = BeanstalkClient

    def __init__(self, app):
        self._app = app

    def buildProtocol(self, addr):
        return self.protocol(self._app)
