"""Infos about objects.
"""
import grokcore.component as grok
import inspect
import types
from persistent import Persistent
from zope.interface import Interface
from zope.proxy import removeAllProxies
from ZODB.utils import p64, u64, tid_repr
from grokui.zodbbrowser.interfaces import IObjectInfo

class ObjectInfo(grok.Adapter):
    """Infos about objects.
    """
    grok.context(Interface)
    grok.implements(IObjectInfo)
    grok.provides(IObjectInfo)

    def __init__(self, context):
        self.obj = removeAllProxies(context)
        self._name = None
        self._parent_oid = None

        
    @property
    def name(self):
        """Get name of wrapped obj.
        """
        if self._name is not None:
            return self._name
        return getattr(self.obj, '__name__', u'???')

    @property
    def parent(self):
        return getattr(self.obj, '__parent__', None)

    def getDescription(self):
        descr = getattr(self.obj, '__doc__', u'')
        descr = inspect.getdoc(self.obj)
        if descr is None:
            return u''
        return descr
    
    def getMembers(self):
        result = []
        for name, obj in inspect.getmembers(self.obj):
            member = IObjectInfo(obj)
            member._name = name
            member._parent_oid = self.oid
            result.append(member)
        return result

    def getValue(self):
        return '%r' % (self.obj, )
    
    @property
    def linkable(self):
        if self.oid is not None:
            return True
        return False

    @property
    def oid(self):
        if not hasattr(self.obj, '_p_oid'):
            return
        if not isinstance(self.obj, Persistent):
            return
        try:
            return u64(self.obj._p_oid)
        except:
            pass
        return

    @property
    def signature(self):
        if inspect.isroutine(self.obj):
            return self.getFunctionSignature()
        if 'method-wrapper' in str(type(self.obj)):
            return self.getFunctionSignature()
        if isinstance(self.obj, types.BuiltinMethodType):
            return "%s(...)" % self.name
        if isinstance(self.obj, types.BuiltinFunctionType):
            return "%s(...)" % self.name
        if isinstance(self.obj, types.MethodType):
            return "%s(...)" % self.name
        return self.name

    @property
    def doc(self):
        descr = inspect.getdoc(self.obj)
        return descr

    @property
    def type_string(self):
        try:
            return str(type(self.obj))
        except:
            pass
        return '<UNKNOWN>'
        
    def getFunctionSignature(self):
        try:
            signature = inspect.formatargspec(*inspect.getargspec(self.obj))
        except TypeError:
            # For certain funcs/methods (C-defined ones, for instance)
            # we cannot get a signature.
            signature = u'(...)'
        
        return '%s%s' % (self.name, signature)
