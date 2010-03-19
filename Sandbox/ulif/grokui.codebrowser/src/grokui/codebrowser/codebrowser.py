"""Code browser pages and other viewing components.
"""
import grok
from grokui.base import IGrokUIRealm, GrokUIView
from zope.component import queryMultiAdapter
from zope.introspector.interfaces import IInfos
from zope.location import LocationProxy
from zope.session.interfaces import ISession
from grokui.codebrowser.namespaceroot import NamespaceRoot

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
            # We set the same location infos for the info
            # object as for its context.
            info = LocationProxy(
                info, codeobj.__parent__, codeobj.__name__
                )
            view = queryMultiAdapter(
                (info, self.request), name='index', default=None)
            if view is None:
                continue
            result.append(view)
        return result

    def traverseParts(self):
        curr = LocationProxy(NamespaceRoot(), self, 'code')
        for name in self.url_path[1:]:
            curr = LocationProxy(curr[name], curr, name)
        return curr

    def getBreadCrumbs(self):
        # XXX: Implement or remove.
        return ''
