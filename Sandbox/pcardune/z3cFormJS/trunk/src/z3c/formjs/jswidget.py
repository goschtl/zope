import zope.component
import zope.interface
from z3c.form.interfaces import IWidget
import interfaces

@zope.component.adapter(interfaces.IJSEvents, IWidget)
@zope.interface.implementer(interfaces.IJSEventsWidget)
def JSEventsWidget(events, widget):
    """Set the events for the widget."""
    widget.jsEvents = events
    if not interfaces.IJSEventsWidget.providedBy(widget):
        zope.interface.alsoProvides(widget, interfaces.IJSEventsWidget)
    return widget
