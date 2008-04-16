from zope import interface, component
from zope.dottedname import resolve

import DateTime
import Acquisition
from OFS import SimpleItem
from Products.ZCatalog import interfaces as zcatalog_ifaces
from Products.PluginIndexes import interfaces as plugidx_ifaces
from Products.PluginIndexes.TextIndex import Vocabulary

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

class MetricsIndex(index.Index, SimpleItem.SimpleItem):
    interface.implements(plugidx_ifaces.IPluggableIndex)

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
        reg(utility_interface, self, utility_name)

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

# XXX Old notes

# This is a tough call.  We can't depend on event ordering
# adding the object to the catalog before the event that adds
# the object to the metric index.

# The solution below is to add the object to the catalog
# without actually indexing it yet so that it has an id in the
# catalog.

# A more appropriate solution might be to fire an event when
# the object is added to the catalog and subscribe to that
# event rather than to IObjectAddedEvent.  This solution would
# involve, however, monkey pacthing CMFCatalogAware.

# So the choice is between monkey patch or abusing the
# catalog.  Until there is obvious reason otherwise, we'll
# abuse the catalog.

# On second thought, let's just make the score index an actual
# index in the catalog
