import os
import glob
import re
import shutil
import zipfile
import time
import base64
import tempfile
import uuid
from zopyx.convert2.convert import Converter
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
            raise IOError('No HTML files found in %s' % tempdir)
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
        return encoded_result

    def convert(self, html_filename, converter_name='pdf-prince'):
        """ Process a single HTML file """

        start_time = time.time()
        c = Converter(html_filename)
        output_filename = c(converter_name)
        file_size = os.stat(output_filename)[6]
        duration = time.time() - start_time
        return output_filename


if __name__ == '__main__':
    from twisted.internet import reactor
    r = Server()
    reactor.listenTCP(7080, server.Site(r))
    reactor.run()

