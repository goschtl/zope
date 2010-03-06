"""ZODBbrowser pages and other viewing components.
"""
import grok
from persistent import Persistent
from zope.component import getMultiAdapter
from zope.security.proxy import removeSecurityProxy
from zope.session.interfaces import ISession
from ZODB.POSException import POSKeyError
from ZODB.utils import p64, u64, tid_repr
from grokui.base import IGrokUIRealm, GrokUIView
from grokui.zodbbrowser.interfaces import IObjectInfo

grok.context(IGrokUIRealm)
grok.templatedir('templates')

class ManageApplications(grok.Permission):
    grok.name('grok.BrowseZODB')

class GrokUIZODBBrowserInfo(GrokUIView):
    grok.name('zodbbrowser')
    grok.template('zodbbrowser')
    grok.require('grok.BrowseZODB')
    grok.title('ZODB browser') # This will appear in grokui menu bar
    grok.order(5) # Position of menu entry will be somewhat to the right

    def publishTraverse(self, request, name):
        self.request.form['oid'] = name
        return self
    
    def update(self, oid=None, show_all=False, show_docs=False, update=None):
        self.obj = None
        if oid is None:
            self.obj = self.context.root
        if self.obj is None:
            try:
                oid = p64(int(self.request.get('oid', self.getRootOID()), 0))
            except ValueError:
                # Invalid number sent
                self.flash(
                    u'Not a valid object ID: %s' % self.request.get('oid'))
                self.redirect(self.url(self.context, '@@zodbbrowser'))
                return
            jar = self.jar()
            try:
                self.obj = jar.get(oid)
            except POSKeyError:
                self.flash(u'No such object ID: %s' % u64(oid))
                self.redirect(self.url(self.context, '@@zodbbrowser'))
                return

        self.info = IObjectInfo(self.obj)
        session = ISession(self.request)['grokui.zodbbrowser']

        self.show_all = show_all
        self.show_docs = show_docs
        if update is None:
            self.show_all = session.get('show_all', False)
            self.show_docs = session.get('show_docs', False)
        session['show_all'] = self.show_all
        session['show_docs'] = self.show_docs
        return
        
    def getRootOID(self):
        """Get OID of root object.
        """
        root = self.jar().root()
        try:
            # The blessed way would be:
            #
            #   root = root[ZopePublication.root_name]
            # 
            # This, however would force us to import zope.app stuff
            # only to get the silly string.
            root = root[u'Application']
        except KeyError:
            pass
        return u64(root._p_oid)

    def jar(self):
        try:
            return self.request.annotations['ZODB.interfaces.IConnection']
        except KeyError:
            obj = removeSecurityProxy(self.context)
            while not isinstance(obj, Persistent):
                obj = removeSecurityProxy(obj.__parent__)
            return obj._p_jar

    def getMemberLink(self, member):
        return "%s/%s" % (self.url(self.context, '@@zodbbrowser'), member.oid)

    def getMemberView(self, member):
        view = getMultiAdapter((member, self.request), name='memberinfo')
        # this subview needs a reference to our context...
        view.parent_context = self.context
        return view

    def getBreadCrumbs(self):
        """Breadcrumb navigation.
        """
        root_oid = self.getRootOID()
        curr = self.info
        parent_list = [curr]
        while True:
            parent = IObjectInfo(curr.getParent())
            if parent.obj is not None:
                parent_list.append(parent)
            if parent.obj is None or parent.obj is curr.obj:
                break
            curr = parent
        link_list = []
        for info in parent_list:
            name = info.name or '???'
            if info.oid == root_oid:
                name = '&lt;root&gt;'
            link = '<a href="%s">%s</a>' % (self.getMemberLink(info), name)
            link_list.append(link)
        if parent_list[-1].oid != root_oid:
            link_list.append('...')
            link_list.append(
                '<a href="%s">%s</a>' % (
                    self.getMemberLink(IObjectInfo(self.context.root)),
                    '&lt;root&gt;'))
        link_list.reverse()
        result = ' / '.join(link_list)
        return result
    
class MemberInfoView(grok.View):
    """View objectinfo as memberinfo.
    """
    grok.name('memberinfo')
    grok.template('memberinfo')
    grok.context(IObjectInfo)
    grok.require('grok.BrowseZODB')

    def update(self):
        session = ISession(self.request)['grokui.zodbbrowser']
        self.show_all = session.get('show_all', False)
        self.show_docs = session.get('show_docs', False)
    
    def getMemberLink(self):
        return "%s/%s" % (
            self.url(self.parent_context, '@@zodbbrowser'),
            self.context.oid)
