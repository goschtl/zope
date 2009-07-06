from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import static

static_view = static('templates/static')

def my_view(context, request):
    return render_template_to_response('templates/mytemplate.pt',
                                       request = request,
                                       project = 'zopyx.smartprintng.server')
def my_view2(context, request):
    return render_template_to_response('templates/mytemplate2.pt',
                                       request = request,
                                       project = 'zopyx.smartprintng.server')
from repoze.bfg.xmlrpc import xmlrpc_view

@xmlrpc_view
def hello(context, request):
    return 'it"me'
