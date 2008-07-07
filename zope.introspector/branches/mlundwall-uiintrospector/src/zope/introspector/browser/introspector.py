from zope.publisher.browser import BrowserView
from zope.app.zapi import getUtility
from zope.dottedname import resolve
from zope.interface import Interface, implements
from zope.traversing.interfaces import ITraversable
from zope.traversing.adapters import DefaultTraversable
from zope.component import adapts

from zope.introspector.interfaces import IRegistryInfo 

class RegistrationView(BrowserView):        
    """
    """
    
    def _expandPath(self, obj):
        module = getattr(obj, '__module__')
        name = getattr(obj, '__name__')
        if module:
            name = '%s.%s' % (module,name)
        return name
    
    def getFactory(self):
        return getattr(self.context.factory, '__name__', '')
    
    def getProvidedInterface(self):
        return self._expandPath(self.context.provided)
    
    def getName(self):
        return self.context.name.split('.')[-1]
    
    def getRequiredInterfaces(self):
        return [self._expandPath(x) for x in self.context.required]
    
class Introspector(BrowserView):
    
    
    def getAll(self):
        return getUtility(IRegistryInfo).getAllInterfaces()
    
    def getUtilities(self):
        return getUtility(IRegistryInfo).getAllUtilities()
    
    def getAdapters(self):
        return getUtility(IRegistryInfo).getAllAdapters()
    
    def getHandlers(self):
        return getUtility(IRegistryInfo).getAllHandlers()
    
    def searchRegistry(self):
        form = self.request.form
        
        search = form.get('searchQuery')
        if not search:
            return
        
        types = []
        if form.get('adapters'):
            types.append('adapters')
        if form.get('utilities'):
            types.append('utilities')
        if form.get('handlers'):
            types.append('handlers')
        if form.get('subscriptionAdapters'):
            types.append('subscriptionAdapters')
        
        registry = getUtility(IRegistryInfo)
        return registry.getRegistrationsForInterface(search, types)
    
    def generateHTMLTree(self):
        return '<ul class="mktree" id="treeBrowse">' + self._generator(self.getAll()) + '</ul>'
    
    def _generator(self, tree):
        page = ""
        tags = {}
        tags['base_start'] = '<ul>'
        tags['base_end'] = '</ul>'
        tags['list_start'] = '<li>'
        tags['list_end'] = '</li>'
        
        if not isinstance(tree, dict):
            return tree
        for key in tree.keys():
            returned = self._generator(tree[key]) 
            if isinstance(returned, str):
                # we are still in the dictionary
                page = page + tags['list_start'] + key
                page = page + tags['base_start']
                page = page + returned 
                page = page + tags['base_end']
                page = page + tags['list_end']
            else:
                # we are at a end node, leaf
                page = page + tags['list_start'] + key
                page = page + '<ul class="interfaceList">'
                
                if isinstance(returned, list):
                    for interface in returned:
                        
                        page = page + tags['list_start'] + str(interface) + tags['list_end']
                        #page = page + tags['list_start'] + self.traverse(interface, '@@registration.html')() + tags['list_end']
                page = page + '</ul>'
                page = page + tags['list_end']
        return page

    def publishTraverse(self, request, name):
        from zope.publisher.interfaces import NotFound
        try:
            return super(Introspector, self).publishTraverse(request, name)
        except NotFound:
            obj = resolve.resolve(name)
            from zope.location.location import LocationProxy
            return LocationProxy(obj, container=self, name=name)
        
    
    