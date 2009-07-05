import base64
import xmlrpclib
import zipfile
import tempfile

# XMLRPC server instance
server = xmlrpclib.Server('http://localhost:7080/')

# send the ZIP archive base64 encoded
zip_data = server.convertZIP(base64.encodestring(file('test.zip', 'rb').read()),
                             'pdf-prince')

# and receive the result PDF as base64 encoded ZIP archive
zip_temp = tempfile.mktemp()
file(zip_temp, 'wb').write(base64.decodestring(zip_data))
ZF = zipfile.ZipFile(zip_temp, 'r')
file('output.pdf', 'wb').write(ZF.read('output.pdf'))
ZF.close()

print 'output.pdf'
