##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

from twisted.web import xmlrpc, server
from base import ServerCore
from logger import LOG

class Server(xmlrpc.XMLRPC, ServerCore):
    """ SmartPrintNG Server (based on Twisted)"""

    def xmlrpc_convertZIP(self, zip_archive, converter_name='pdf-prince'):
        """ Process html-file + images within a ZIP archive """

        try:
            return self.convertZIP(zip_archive, converter_name)
        except Exception, e:
            msg = 'Conversion failed (%s)' % e
            LOG.error(msg, exc_info=True)
            return xmlrpc.Fault(123, msg)

def main():
    from twisted.internet import reactor
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", type="int",
                      help="port", default=7080)

    (options, args) = parser.parse_args()
    LOG.debug('Started SmartPrintNG XMLRPC server(port %d)' % options.port)
    r = Server()
    reactor.listenTCP(options.port, server.Site(r))
    reactor.run()

if __name__ == '__main__':
    main()
