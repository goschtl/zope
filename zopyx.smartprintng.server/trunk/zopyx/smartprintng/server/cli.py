from twisted.web import xmlrpc, server

class Server(xmlrpc.XMLRPC):
    """ SmartPrintNG Server """

    def xmlrpc_echo(self, x):
        """
        Return all passed args.
        """
        return x


if __name__ == '__main__':
    from twisted.internet import reactor
    r = Server()
    reactor.listenTCP(7080, server.Site(r))
    reactor.run()

