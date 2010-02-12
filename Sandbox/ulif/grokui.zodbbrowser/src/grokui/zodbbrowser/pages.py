"""ZODBbrowser pages.
"""
import grok
from persistent import Persistent
from zope.security.proxy import removeSecurityProxy
from ZODB.utils import p64, u64, tid_repr
from grokui.base import IGrokUIRealm, GrokUIView
from grokui.zodbbrowser.interfaces import IObjectInfo
from grokui.zodbbrowser.objectinfo import MemberInfo

grok.context(IGrokUIRealm)
grok.templatedir('templates')

class ManageApplications(grok.Permission):
    grok.name('grok.ManageApplications')

class GrokUIZODBBrowserInfo(GrokUIView):
    grok.name('zodbbrowser')
    grok.template('zodbbrowser')
    grok.require('grok.ManageApplications')

    def update(self, oid=None, name=None):
        self.obj = None
        if oid is None:
            self.obj = self.context.root
            #self.obj = self.findClosestPersistent()
        if self.obj is None:
            oid = p64(int(self.request.get('oid', self.getRootOID()), 0))
            jar = self.jar()
            self.obj = jar.get(oid)
        self.info = IObjectInfo(self.obj)
        self.info.name = name

    def findClosestPersistent(self):
        obj = removeSecurityProxy(self.context)
        while not isinstance(obj, Persistent):
            try:
                obj = obj.__parent__
            except AttributeError:
                return None
        return obj

    def getRootOID(self):
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
        return self.url(self.context, '@@zodbbrowser',
                        data = dict(oid=member.oid,name=member.name))
