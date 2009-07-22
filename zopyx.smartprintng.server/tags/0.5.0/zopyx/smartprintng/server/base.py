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
from logger import LOG
import mail_util
from zopyx.convert2.convert import Converter

temp_directory = os.path.join(tempfile.gettempdir(), 
                              'zopyx.smartprintng.server')
if not os.path.exists(temp_directory):
    os.makedirs(temp_directory)


class ServerCore(object):
    """ SmartPrintNG Server Core Implementation """

    def _inject_base_tag(self, html_filename):
        """ All input HTML files contain relative urls (relative
            to the path of the main HTML file (the "working dir").
            So we must inject a BASE tag in order to call the external
            converters properly with the full path of the html input file
            since we do not want to change the process working dir (not
            acceptable in a multi-threaded environment).
            ATT: this should perhaps handled within zopyx.convert2
        """
        html = file(html_filename).read()
        pos = html.lower().find('<head>')
        html = html[:pos] + '<head><base href="%s"/>' % html_filename + html[pos+6:]
        file(html_filename, 'wb').write(html)

    def _convert(self, html_filename, converter_name='pdf-prince'):
        """ Process a single HTML file """
        return Converter(html_filename)(converter_name)

    def _processZIP(self, zip_archive, converter_name):

        # temp direcotry handling 
        now = datetime.now().strftime('%Y%m%d%Z%H%M%S')
        ident = '%s-%s' % (now, uuid.uuid4())
        tempdir = os.path.join(temp_directory, ident)
        os.makedirs(tempdir)

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
        # inject BASE tag containing the full local path (required by PrinceXML)
        self._inject_base_tag(html_filename)
        result = self._convert(html_filename, 
                               converter_name=converter_name)
        basename, ext = os.path.splitext(os.path.basename(result))

        # Generate result ZIP archive with base64-encoded result
        zip_out = os.path.join(tempdir, 'output.zip')
        ZF = zipfile.ZipFile(zip_out, 'w')
        ZF.writestr('output%s' % ext, file(result, 'rb').read())
        ZF.close()
        return zip_out, result

    def convertZIP(self, zip_archive, converter_name='pdf-prince'):
        """ Process html-file + images within a ZIP archive """

        LOG.info('Incoming request (%s, %d bytes)' % (converter_name, len(zip_archive)))
        ts = time.time()
        zip_out, output_filename = self._processZIP(zip_archive, converter_name)
        encoded_result = base64.encodestring(file(zip_out, 'rb').read())
        shutil.rmtree(os.path.dirname(zip_out))
        LOG.info('Request end (%3.2lf seconds)' % (time.time() - ts))
        return encoded_result

    def convertZIPEmail(self, zip_archive, converter_name='pdf-prince', sender=None, recipient=None, subject=None, body=None):
        """ Process zip archive and send conversion result as mail """

        LOG.info('Incoming request (%s, %d bytes)' % (converter_name, len(zip_archive)))
        ts = time.time()
        zip_out, output_filename = self._processZIP(zip_archive, converter_name)
        mail_util.send_email(sender, recipient, subject, body, [output_filename])
        shutil.rmtree(os.path.dirname(zip_out))
        LOG.info('Request end (%3.2lf seconds)' % (time.time() - ts))
        return True

    def availableConverters(self):
        from zopyx.convert2.registry import availableConverters
        return availableConverters()

if __name__ == '__main__':
    s = ServerCore()
    print s.availableConverters() 
