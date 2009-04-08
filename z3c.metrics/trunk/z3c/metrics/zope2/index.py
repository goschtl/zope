from zope import interface, component
from zope.dottedname import resolve

import DateTime
import Acquisition
from OFS import SimpleItem
from Products.ZCatalog import interfaces as zcatalog_ifaces
from Products.PluginIndexes import interfaces as plugidx_ifaces
from Products.PluginIndexes.TextIndex import Vocabulary
from Products.GenericSetup import interfaces as gs_ifaces
from Products.GenericSetup.PluginIndexes import exportimport

from z3c.metrics import interfaces, index
from z3c.metrics.zope2 import scale

class IRemoveScoreEvent(interfaces.IRemoveValueEvent):
    """Remove the object score from the index."""

class IAddSelfValueEvent(interfaces.IAddValueEvent):
    """Add self value with special handling for the index."""
    # This is necessary because for the OFS/CMF/ZCatalog mess we need
    # the self add handlers to trigger for initial indexing and
    # rebuilding scores but not on object add

class InitIndexScoreEvent(index.IndexesScoreEvent):
    interface.implements(interfaces.IInitScoreEvent,
                         IAddSelfValueEvent)

class RemoveIndexScoreEvent(index.IndexesScoreEvent):
    interface.implements(IRemoveScoreEvent)

class IMetricsIndex(interfaces.IIndex,
                    plugidx_ifaces.IPluggableIndex):
    """sro"""

class MetricsIndex(index.Index, SimpleItem.SimpleItem):
    """A Metrics Index in a ZCatalog"""
    interface.implements(IMetricsIndex)

    def __init__(self, id, extra=None, caller=None):
        self.id = id
        self.__catalog_path = caller.getPhysicalPath()

        if extra is None:
            extra = Vocabulary._extra()

        # TODO: the utility registration should be moved to an INode
        # GS handler to be run after the index is added
        utility_interface = extra.__dict__.pop(
            'utility_interface', interfaces.IIndex)
        utility_name = extra.__dict__.pop('utility_name', '')

        scale_kw = {}
        if 'start' in extra.__dict__:
            scale_kw['start'] = DateTime.DateTime(
                extra.__dict__.pop('start'))
        if 'scale_unit' in extra.__dict__:
            scale_kw['scale_unit'] = float(
                extra.__dict__.pop('scale_unit'))
        index_scale = scale.ExponentialDateTimeScale(**scale_kw)

        super(MetricsIndex, self).__init__(
            scale=index_scale, **extra.__dict__)

        if isinstance(utility_interface, (str, unicode)):
            utility_interface = resolve.resolve(utility_interface)
        if not utility_interface.providedBy(self):
            interface.alsoProvides(self, utility_interface)
        sm = component.getSiteManager(context=caller)
        reg = getattr(sm, 'registerUtility', None)
        if reg is None:
            reg = sm.provideUtility
        reg(component=self, provided=utility_interface,
            name=utility_name)

    def _getCatalog(self):
        zcatalog = Acquisition.aq_parent(Acquisition.aq_inner(
            Acquisition.aq_parent(Acquisition.aq_inner(self))))
        if not zcatalog_ifaces.IZCatalog.providedBy(zcatalog):
            return self.restrictedTraverse(self.__catalog_path)
        return zcatalog

    def _getKeyFor(self, obj):
        """Get the key from the ZCatalog so that the index may be used
        to score or sort ZCatalog results."""
        return self._getCatalog().getrid(
            '/'.join(obj.getPhysicalPath()))

    def index_object(self, documentId, obj, threshold=None):
        """Run the initialize score metrics for this index only if
        this is the first time the object is indexed."""
        if documentId not in self._scores:
            obj = self._getCatalog().getobject(documentId)
            event = InitIndexScoreEvent(obj, [self])
            component.subscribers([obj, event], None)
            return True
        return False

    def unindex_object(self, documentId):
        """Run the remove value metrics for this index only when the
        object is unindexed."""
        obj = self._getCatalog().getobject(documentId)
        event = RemoveIndexScoreEvent(obj, [self])
        component.subscribers([obj, event], None)

class MetricsIndexNodeAdapter(exportimport.PluggableIndexNodeAdapter):
    component.adapts(IMetricsIndex, gs_ifaces.ISetupEnviron)

    __used_for__ = interfaces.IIndex

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('index')
        return node

    def _importNode(self, node):
        """Prevent the index from being cleared.
        """
        pass

    node = property(_exportNode, _importNode)
