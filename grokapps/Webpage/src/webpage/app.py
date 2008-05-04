import grok
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.publisher.browser import applySkin


##
## The application
##

class Webpage(grok.Application, grok.Container):
    pass

#
# Views for this application
# 

class Index(grok.View):
    pass # see app_templates/index.pt

class About(grok.View):
    pass

class HeaderFooter(grok.View):
    pass



##
## The mobile layer
##


class MobileLayer(IDefaultBrowserLayer):
    pass

class MobileSkin(grok.Skin):
    grok.name('mobile') # optional
    grok.layer(MobileLayer)
    
#
# Views in this layer
#
    
class MobileHeaderFooter(grok.View):
    grok.name('headerfooter') # important
    grok.layer(MobileLayer)

class MobileIndex(grok.View):
    grok.name('index')
    grok.layer(MobileLayer)


        

@grok.subscribe(Webpage, IBeforeTraverseEvent)
def handle(obj, event):
    if event.request.get('HTTP_USER_AGENT').find('Nokia') > -1:
        applySkin(event.request, MobileLayer)