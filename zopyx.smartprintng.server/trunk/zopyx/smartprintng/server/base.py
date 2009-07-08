##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import base64
import glob
import os
import shutil
import tempfile
from datetime import datetime
import time
import uuid
import zipfile
from zopyx.convert2.convert import Converter
from logger import LOG

temp_directory = os.path.join(tempfile.gettempdir(), 
                              'zopyx.smartprintng.server')
if not os.path.exists(temp_directory):
    os.makedirs(temp_directory)


class ServerCore(object):
    """ SmartPrintNG Server Core Implementation """

    def convertZIP(self, zip_archive, converter_name='pdf-prince'):
        """ Process html-file + images within a ZIP archive """

        now = datetime.now().strftime('%Y%m%d%Z%H%M%S')
        ident = '%s-%s' % (now, uuid.uuid4())
        tempdir = os.path.join(temp_directory, ident)
        os.makedirs(tempdir)
        LOG.debug('Incoming request (%s, %d bytes, %s)' % (converter_name, len(zip_archive), tempdir))
        ts = time.time()
        # store zip archive first
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
        result = self._convert(html_filename, 
                               converter_name=converter_name)
        basename, ext = os.path.splitext(os.path.basename(result))

        # Generate result ZIP archive with base64-encoded result
        zip_out = os.path.join(tempdir, 'output.zip')
        ZF = zipfile.ZipFile(zip_out, 'w')
        ZF.writestr('output%s' % ext, file(result, 'rb').read())
        ZF.close()
        encoded_result = base64.encodestring(file(zip_out, 'rb').read())
        shutil.rmtree(tempdir)
        LOG.debug('Request end (%3.2lf seconds)' % (time.time() -ts))
        return encoded_result

    def _convert(self, html_filename, converter_name='pdf-prince'):
        """ Process a single HTML file """
        return Converter(html_filename)(converter_name)

    def availableConverters(self):
        from zopyx.convert2.registry import availableConverters
        return availableConverters()

if __name__ == '__main__':
    s = ServerCore()
    print s.availableConverters() 
