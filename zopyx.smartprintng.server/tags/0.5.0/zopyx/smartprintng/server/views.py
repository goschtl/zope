##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import pkg_resources
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static
from repoze.bfg.view import bfg_view
from zopyx.smartprintng.server.base import ServerCore
from models import Server
from logger import LOG

static_view = static('templates/static')

##################
# HTTP views
##################

@bfg_view(for_=Server, request_type='GET', permission='read')
class index(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        converters = ServerCore().availableConverters()
        version = pkg_resources.require('zopyx.smartprintng.server')[0].version 
        return render_template_to_response('templates/index.pt',
                                           converters=converters,
                                           request=self.request,
                                           version=version,
                                           project='zopyx.smartprintng.server')

##################
# XMLRPC views
##################

from repoze.bfg.xmlrpc import xmlrpc_view
import xmlrpclib

@bfg_view(name='convertZIP', for_=Server)
@xmlrpc_view
def convertZIP(context, zip_archive, converter_name='pdf-prince'):
    core = ServerCore()
    try:
        return core.convertZIP(zip_archive, converter_name)
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)


@bfg_view(name='convertZIPEmail', for_=Server)
@xmlrpc_view
def convertZIPEmail(context, zip_archive, converter_name='pdf-prince', sender=None, recipient=None, subject=None, body=None):
    core = ServerCore()
    try:
        return core.convertZIPEmail(zip_archive, converter_name, sender, recipient, subject, body)
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)


@bfg_view(name='availableConverters', for_=Server)
@xmlrpc_view
def availableConverters(context):
    return ServerCore().availableConverters()


@bfg_view(name='ping', for_=Server)
@xmlrpc_view
def ping(context):
    return 'zopyx.smartprintng.server'

