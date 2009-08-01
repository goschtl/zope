##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import time
import tempfile
import shutil
import mimetypes
import xmlrpclib
import pkg_resources
from stat import ST_CTIME
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static
from repoze.bfg.view import bfg_view
from repoze.bfg.xmlrpc import xmlrpc_view
from webob import Response
from models import Server
from logger import LOG

static_view = static('templates/static')

spool_directory = os.path.join(tempfile.gettempdir(), 
                              'zopyx.smartprintng.server-spool')
if not os.path.exists(spool_directory):
    os.makedirs(spool_directory)

##################
# HTTP views
##################

@bfg_view(for_=Server, request_type='GET', permission='read')
class index(object):
    """ The default view providing some system information """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        converters = self.context.availableConverters()
        version = pkg_resources.require('zopyx.smartprintng.server')[0].version 
        return render_template_to_response('templates/index.pt',
                                           context=self.context,
                                           converters=converters,
                                           request=self.request,
                                           version=version,
                                           project='zopyx.smartprintng.server')


@bfg_view(for_=Server, name='deliver')
def deliver(context, request):
    """ Send out a generated output file """

    filename = request.params['filename']
    prefix = request.params.get('prefix')
    dest_filename = os.path.abspath(os.path.join(spool_directory, filename))

    # various (security) checks
    if not os.path.exists(dest_filename):
        return Response(status=404)

    if not dest_filename.startswith(spool_directory):
        return Response(status=404)

    if time.time() - os.stat(dest_filename)[ST_CTIME] >= context.delivery_max_age:
        return Response(status=404)

    ct, dummy = mimetypes.guess_type(dest_filename)
    filename = os.path.basename(filename)
    if prefix:
        filename = prefix + os.path.splitext(filename)[1]
    headers = [('content-disposition','attachment; filename=%s' % filename),
               ('content-type', ct)]
    return Response(body=file(dest_filename, 'rb').read(),
                    content_type=ct,
                    headerlist=headers
                    )


##################
# XMLRPC views
##################


@bfg_view(name='convertZIP', for_=Server)
@xmlrpc_view
def convertZIP(context, zip_archive, converter_name='pdf-prince'):
    try:
        return context.convertZIP(zip_archive, converter_name)
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)


@bfg_view(name='convertZIPEmail', for_=Server)
@xmlrpc_view
def convertZIPEmail(context, zip_archive, converter_name='pdf-prince', sender=None, recipient=None, subject=None, body=None):
    try:
        return context.convertZIPEmail(zip_archive, converter_name, sender, recipient, subject, body)
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)


@bfg_view(name='convertZIPandRedirect',  for_=Server)
@xmlrpc_view
def convertZIPandRedirect(context, zip_archive, converter_name='prince-pdf', prefix=None):
    """ This view appects a ZIP archive through a POST request containing all
        relevant information (similar to the XMLRPC API). However the converted
        output file is not returned to the caller but delivered "directly" through
        the SmartPrintNG server (through an URL redirection). The 'prefix'
        parameter can be used to override the basename of filename used within the
        content-disposition header.
        (This class is only a base class for the related http_ and xmlrpc_
         view (in order to avoid redudant code).)
    """

    try:
        output_archivename, output_filename = context._processZIP(zip_archive, converter_name)
        output_ext = os.path.splitext(output_filename)[1]

        # take ident from archive name
        ident = os.path.splitext(os.path.basename(output_archivename))[0]

        # move output file to spool directory
        dest_filename = os.path.join(spool_directory, '%s%s' % (ident, output_ext))
        rel_output_filename = dest_filename.replace(spool_directory + os.sep, '')
        shutil.move(output_filename, dest_filename)
        host = 'localhost'
        port = 6543
        prefix = prefix or ''
        location = 'http://%s:%s/deliver?filename=%s&prefix=%s' % (host, port, rel_output_filename, prefix)
        return location
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)


@bfg_view(name='availableConverters', for_=Server)
@xmlrpc_view
def availableConverters(context):
    return context.availableConverters()


@bfg_view(name='ping', for_=Server)
@xmlrpc_view
def ping(context):
    return 'zopyx.smartprintng.server'

