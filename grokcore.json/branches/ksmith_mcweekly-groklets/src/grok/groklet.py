import grok

from zope import interface, component
from zope.traversing.interfaces import IPathAdapter
from zope.tales.interfaces import ITALESFunctionNamespace
from zope.security.proxy import removeSecurityProxy

from interfaces import IGroklet
import operator



class GrokletTalesAPIAdapter(object):
    interface.implements(ITALESFunctionNamespace, IPathAdapter)


    def __init__(self, context):
        self.context= context

    def setEngine(self, engine):
        # make request and view available
        self.request = removeSecurityProxy(engine.vars['request'])
        self.view = removeSecurityProxy(engine.vars['view'])

    def getGroklets(self, name):
        groklets = list(component.getAdapters(
            (self.context,
             self.request,
             self.view,
             self.view), 
            IGroklet))

        for name, groklet in groklets:
            print name, groklet.__view_name__
                # keep only the groklets: with the right name
                # e.g. /groklets:center  _groklet_name == 'center'
                # if __view_name goes bye bye, create a __groklet_name
        groklets = [groklet for gname, groklet in list(groklets) if getattr(groklet, '__view_name__', None) == name ]
        return groklets 

    def __getattr__(self, name):

        # XXX: skip private methods, is there a better way to handle this?
        if not name.startswith('__'):

            # gather all /groklets:
            
            groklets = self.getGroklets(name)
            
            groklets = sorted( groklets,
                               key=operator.attrgetter('order'))

            results = []

            # XXX: This could also be split into an update, then render pass
            # XXX: Catch errors
            for groklet in groklets:
                try:
                    result = groklet()
                except:
                    # XXX: Area for improvement
                    # XXX: viewlets ignore errors and render the page
                    # this is a stab at rendering the error as output
                    # to the viewlet, not a good default, but here as
                    # a reminder, since tracking down viewlet errors
                    # are a big pain
                    import sys
                    exc_info = sys.exc_info()
                    result = "<b>%s</b><p>%s</p><p>%s</p>" % (exc_info[0], exc_info[1], exc_info[2] )

                results.append( result )
                    
            return '\n'.join(results)
        
