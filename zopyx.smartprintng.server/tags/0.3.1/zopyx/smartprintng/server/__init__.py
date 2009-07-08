# A package


# Monkey patches

import xmlrpclib
def parse_xmlrpc_request(request):
    """ original code without DOS check """
    params, method = xmlrpclib.loads(request.body)
    return params, method

import repoze.bfg.xmlrpc
repoze.bfg.xmlrpc.parse_xmlrpc_request = parse_xmlrpc_request


