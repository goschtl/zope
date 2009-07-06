from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static


def index(context, request):
    return render_template_to_response('templates/index.pt',
                                       request = request,
                                       project = 'zopyx.smartprintng.server')

from repoze.bfg.xmlrpc import xmlrpc_view

@xmlrpc_view
def convertZIP(context, zip_archive, converter_name='pdf_prince'):

    from base import ServerCore
    core = ServerCore()
    return core.convertZIP(zip_archive, converter_name)
