##########################################################################
# zopyx.smartprintng.client - client library for the SmartPrintNG server
# (C) 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import sys
import base64
import xmlrpclib
import zipfile
import tempfile
import zipfile

def convertZIP(dirname, converter_name='pdf-prince', host='localhost', port=6543):
    """ XMLRPC client to SmartPrintNG server """
    cwd = os.getcwd()
    os.chdir(dirname)
    server = xmlrpclib.ServerProxy('http://%s:%d/convertZIP' % (host, port))
    zip_filename = tempfile.mktemp()
    ZF = zipfile.ZipFile(zip_filename, 'w')
    for fname in os.listdir('.'):
        if not os.path.isfile(fname):
            continue
        fullname = os.path.join(dirname, fname)
        ZF.write(fname)
    ZF.close()

    # send the ZIP archive base64 encoded
    zip_data = server.convertZIP(base64.encodestring(file(zip_filename, 'rb').read()),
                                 converter_name)

    # and receive the result PDF as base64 encoded ZIP archive
    zip_temp = tempfile.mktemp()
    file(zip_temp, 'wb').write(base64.decodestring(zip_data))
    ZF = zipfile.ZipFile(zip_temp, 'r')
    names = ZF.namelist()
    output_filename = os.path.abspath(names[0])
    file(output_filename, 'wb').write(ZF.read(names[0]))
    ZF.close()
    os.unlink(zip_filename)
    os.unlink(zip_temp)
    os.chdir(cwd)
    return output_filename

if __name__ == '__main__':
    # usage: convertZIP <dirname>
    print convertZIP(sys.argv[1])

