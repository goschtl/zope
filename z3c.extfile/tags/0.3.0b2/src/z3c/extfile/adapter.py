from zope import component
from zope import interface
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.http import IResult
import interfaces
from zope.security.proxy import removeSecurityProxy
from zope.app.wsgi.fileresult import FallbackWrapper
from zope.publisher.http import DirectResult

@component.adapter(interfaces.IReadFile, IHTTPRequest)
@interface.implementer(IResult)
def ReadFileResult(f, request):
    f = removeSecurityProxy(f)
    f.seek(0)

    if request.response.getHeader('content-length') is None:
        size=len(f)
        request.response.setHeader('Content-Length', str(size))
        
    wrapper = request.environment.get('wsgi.file_wrapper')
    if wrapper is not None:
        f = wrapper(f)
    else:
        f = FallbackWrapper(f)
    return DirectResult(f)
