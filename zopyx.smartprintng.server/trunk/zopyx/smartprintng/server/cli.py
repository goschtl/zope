import base64
import glob
import os
import re
import shutil
import tempfile
import time
import uuid
import zipfile
from zopyx.convert2.convert import Converter
from zopyx.convert2.logger import LOG
from twisted.web import xmlrpc, server

tempdir = tempfile.mkdtemp(prefix='zopyx.smartprintng.server')

class Server(xmlrpc.XMLRPC):
    """ SmartPrintNG Server """

    rxcountpages = re.compile(r"$\s*/Type\s*/Page[/\s]", re.MULTILINE|re.DOTALL)

    def _countPages(self, filename):
        data = file(filename,"rb").read()
        return len(self.rxcountpages.findall(data))

    def xmlrpc_convertZIP(self, zip_archive, converter_name='pdf-prince'):
        """ Process html-file + images within a ZIP archive """

        def _convertZIP(zip_archive, converter_name):

            LOG.debug('Incoming request (%s, %d)' % (converter_name, len(zip_archive)))
            ts = time.time()
            # store zip archive first
            tempdir = tempfile.mkdtemp()
            zip_temp = os.path.join(tempdir, 'input.zip')
            file(zip_temp, 'wb').write(base64.decodestring(zip_archive))
            ZF = zipfile.ZipFile(zip_temp, 'r')
            for name in ZF.namelist():
                destfile = os.path.join(tempdir, name)
                if not os.path.exists(os.path.dirname(destfile)):
                    os.makedirs(os.path.dirname(destfile))
                file(destfile, 'wb').write(ZF.read(name))
            ZF.close()

            # find HTML file
            html_files = glob.glob(os.path.join(tempdir, '*.htm*'))
            if not html_files:
                raise IOError('Archive does not contain any html files')
            if len(html_files) > 1:
                raise RuntimeError('Archive contains more than one html file')
            html_filename = html_files[0]
            result = self.convert(html_filename, 
                                  converter_name=converter_name)

            # Generate result ZIP archive with base64-encoded result
            zip_out = os.path.join(tempdir, 'output.zip')
            ZF = zipfile.ZipFile(zip_out, 'w')
            ZF.writestr('output.pdf', file(result, 'rb').read())
            ZF.close()
            encoded_result = base64.encodestring(file(zip_out, 'rb').read())
            shutil.rmtree(tempdir)
            LOG.debug('request end (%3.2lf seconds)' % (time.time() -ts))
            return encoded_result

        try:
            return _convertZIP(zip_archive, converter_name)
        except Exception, e:
            msg = 'Conversion failed (%s)' % e
            LOG.error(msg, exc_info=True)
            return xmlrpc.Fault(123, msg)

    def convert(self, html_filename, converter_name='pdf-prince'):
        """ Process a single HTML file """
        return Converter(html_filename)(converter_name)


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
