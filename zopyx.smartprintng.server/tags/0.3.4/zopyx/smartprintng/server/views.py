##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static
from zopyx.smartprintng.server.base import ServerCore
from logger import LOG

static_view = static('templates/static')

##################
# HTTP views
##################

class index(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        converters = ServerCore().availableConverters()
        return render_template_to_response('templates/index.pt',
                                           converters=converters,
                                           request=self.request,
                                           project='zopyx.smartprintng.server')

##################
# XMLRPC views
##################

from repoze.bfg.xmlrpc import xmlrpc_view
import xmlrpclib

@xmlrpc_view
def convertZIP(context, zip_archive, converter_name='pdf-prince'):
    core = ServerCore()
    try:
        return core.convertZIP(zip_archive, converter_name)
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)

@xmlrpc_view
def availableConverters(context):
    return ServerCore().availableConverters()

@xmlrpc_view
def ping(context):
    return 'zopyx.smartprintng.server'

