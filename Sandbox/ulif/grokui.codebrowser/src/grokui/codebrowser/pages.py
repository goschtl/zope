"""Code browser pages and other viewing components.
"""
import grok
import pkg_resources
from martian.scan import module_info_from_dotted_name
from zope.component import getMultiAdapter
from zope.introspector.code import Code, Package, Module
from zope.introspector.interfaces import IInfo, IInfos
from zope.location import LocationProxy
from zope.session.interfaces import ISession

from grokui.base import IGrokUIRealm, GrokUIView

grok.context(IGrokUIRealm)
grok.templatedir('templates')

class BrowseCodePermission(grok.Permission):
    grok.name('grok.BrowseCode')

class GrokUICodeBrowser(GrokUIView):
    grok.name('codebrowser')
    grok.template('codebrowser')
    grok.require('grok.BrowseCode')
    grok.title('Code browser') # This will appear in grokui menu bar
    grok.order(8) # Position of menu entry will be somewhat to the right

    url_path = []

    def publishTraverse(self, request, name):
        self.url_path = request.getTraversalStack() + [name]
        request.setTraversalStack([])
        self.url_path.reverse()
        return self

    def update(self, show_all=False, show_docs=False, update=None):

        session = ISession(self.request)['grokui.codebrowser']
        if update is None:
            show_all = session.get('show_all', False)
            show_docs = session.get('show_docs', False)
        self.show_all = session['show_all'] = show_all
        self.show_docs = session['show_docs'] = show_docs

        self.path = '/'.join(self.url_path)
        self.infos = []
        self.info_views = []
        if not self.url_path:
            self.url_path = ['code']
        if self.url_path[0] == 'code':
            obj = self.traverseParts()
            self.info_views = self.getInfoViewsForCode(obj)

    def getInfoViewsForCode(self, codeobj):
        result = []
        infos = IInfos(codeobj).infos()
        for name, info in infos:
            view = None
            try:
                # We set the same location infos for the info
                # object as for its context.
                info = LocationProxy(
                    info, codeobj.__parent__, codeobj.__name__
                    )
                result.append(
                    getMultiAdapter((info, self.request), name='index')
                    )
            except:
                # No view available for that info...
                pass
        return result

    def traverseParts(self):
        curr = LocationProxy(NamespaceRoot(), self, 'code')
        for name in self.url_path[1:]:
            curr = LocationProxy(curr[name], curr, name)
        return curr

    def getBreadCrumbs(self):
        return ''

class NamespaceRoot(Code):
    def __init__(self, dotted_name=''):
        self.dotted_name = ''
        
    def __getitem__(self, name):
        sub_module = None
        try:
            sub_module = module_info_from_dotted_name(name)
        except ImportError:
            # No module of that name found. The name might denote
            # something different like a file or be really trash.
            pass
        if sub_module is None:
            raise KeyError
        if sub_module.isPackage():
            return Package(sub_module.dotted_name)
        return Module(sub_module.dotted_name)

class NamespaceRootInfo(grok.Adapter):
    grok.context(NamespaceRoot)
    grok.provides(IInfo)
    grok.name('coderoot')
    
    def getDottedName(self):
        return self.context.dotted_name

    def getSubItems(self):
        importables = pkg_resources.Environment()
        top_level_pkgs = [x.split('.')[0] for x in importables]
        top_level_pkgs = sorted(list(set(top_level_pkgs)))
        for pkg in top_level_pkgs:
            yield pkg

    def _filterSubItems(self, filter=lambda x: True):
        for name in self.getSubItems():
            try:
                info = module_info_from_dotted_name(name)
                if filter and filter(info):
                    yield info
            except ImportError:
                pass
            except AttributeError:
                # This is thrown sometimes by martian.scan if an
                # object lacks a __file__ attribute and needs further
                # investigation.
                pass
        
    def getSubPackages(self):
        return sorted(self._filterSubItems(lambda x: x.isPackage()),
                      key=lambda x:x.dotted_name)

    def getModules(self):
        return sorted(self._filterSubItems(lambda x: not x.isPackage()))

class NamespaceRootInfoView(grok.View):
    grok.context(NamespaceRootInfo)
    grok.require('grok.BrowseCode')
    grok.name('index')
    grok.template('rootinfo')

    def item_url(self, info):
        return self.url(LocationProxy(info, self.context, info.dotted_name))
