"""ZODBbrowser pages and other viewing components.
"""
import grok
from persistent import Persistent
from zope.component import getMultiAdapter
from zope.location import LocationProxy
from zope.security.proxy import removeSecurityProxy
from zope.session.interfaces import ISession
from ZODB.POSException import POSKeyError
from ZODB.utils import p64, u64, tid_repr

from grokui.base import IGrokUIRealm, GrokUIView
from grokui.zodbbrowser.interfaces import IObjectInfo, IBTreeInfo

grok.context(IGrokUIRealm)
grok.templatedir('templates')

class BrowseZODBPermission(grok.Permission):
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

    def jar(self):
        try:
            return self.request.annotations['ZODB.interfaces.IConnection']
        except KeyError:
            obj = removeSecurityProxy(self.context)
            while not isinstance(obj, Persistent):
                obj = removeSecurityProxy(obj.__parent__)
            return obj._p_jar

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

    def getObjectAndOID(self, oid=None):
        """Compute associated object and its OID.
        """
        obj = None
        if oid is None:
            obj = self.context.root
        if obj is None:
            oid = p64(int(self.request.get('oid', self.getRootOID()), 0))
            obj = self.jar().get(oid)
        return (obj, oid)

    def update(self, oid=None, show_all=False, show_docs=False, update=None):
        try:
            self.obj, self.oid = self.getObjectAndOID(oid=oid)
        except (POSKeyError, ValueError):
            # Invalid number sent
            self.flash(
                u'Not a valid object ID: %s' % self.request.get('oid'))
            self.redirect(self.url(self.context, '@@zodbbrowser'))
            return

        info = IObjectInfo(self.obj)
        self.info = LocationProxy(info, self, str(info.oid))

        session = ISession(self.request)['grokui.zodbbrowser']
        if update is None:
            show_all = session.get('show_all', False)
            show_docs = session.get('show_docs', False)
        self.show_all = session['show_all'] = show_all
        self.show_docs = session['show_docs'] = show_docs
        return

    def getBreadCrumbs(self):
        """Breadcrumb navigation.
        """
        root_oid = self.getRootOID()
        curr = self.info
        b_list = []
        while True:
            link = self.getMemberLink(curr)
            name = curr.name or '???'
            if curr.oid == root_oid:
                name = '&lt;root&gt;'
            b_list.append('<a href="%s">%s</a>' % (link, name))
            if curr.parent is None or curr.parent is curr.obj:
                break
            curr = IObjectInfo(curr.parent)
        if curr.oid != root_oid:
            b_list.append('...')
            b_list.append('<a href="%s">%s</a>' % (
                    self.getMemberLink(IObjectInfo(self.context.root)),
                    '&lt;root&gt;'))
        b_list.reverse()
        return ' / '.join(b_list)

    def getMemberLink(self, memberinfo):
        return self.url(
            LocationProxy(memberinfo, self, str(memberinfo.oid)))

class ObjectInfoView(grok.View):
    grok.name('index')
    grok.require('grok.BrowseZODB')
    grok.context(IObjectInfo)

    def update(self):
        session = ISession(self.request)['grokui.zodbbrowser']
        self.show_all = session.get('show_all', False)
        self.show_docs = session.get('show_docs', False)

    def getMemberView(self, member=None):
        if member is None:
            member = self.context
        member = LocationProxy(
            member, self.context.__parent__, str(member.oid))
        view = getMultiAdapter((member, self.request), name='memberinfo')
        return view

class FolderInfoView(ObjectInfoView):
    grok.name('index')
    grok.require('grok.BrowseZODB')
    grok.context(IBTreeInfo)
    grok.template('objectinfoview')

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
        return self.url(self.context)
