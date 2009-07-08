##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static
from logger import LOG

static_view = static('templates/static')

def index(context, request):
    return render_template_to_response('templates/index.pt',
                                       request = request,
                                       project = 'zopyx.smartprintng.server')

from repoze.bfg.xmlrpc import xmlrpc_view
import xmlrpclib

@xmlrpc_view
def convertZIP(context, zip_archive, converter_name='pdf-prince'):
    from zopyx.smartprintng.server.base import ServerCore
    core = ServerCore()
    try:
        return core.convertZIP(zip_archive, converter_name)
    except Exception, e:
        msg = 'Conversion failed (%s)' % e
        LOG.error(msg, exc_info=True)
        return xmlrpclib.Fault(123, msg)

@xmlrpc_view
def availableConverters(context):
    from zopyx.smartprintng.server.base import ServerCore
    return ServerCore().availableConverters()

