import grok
from hurry import yui
from hurry.resource import NeededInclusions
from zope import interface

from zope.introspector.interfaces import IObjectInfo
from zope.introspector.viewinfo import ViewInfo
from grokui.introspector.util import dotted_name_url


class Inspect(grok.View):
    grok.context(interface.Interface)
    
    _objectinfo = None
    
    def getObjectInfo(self):
        if self._objectinfo is None:
            self._objectinfo = IObjectInfo(self.context)
        return self._objectinfo

    def getTypeName(self):
        mod = getattr(self.context, '__module__', '')
        name = getattr(self.context, '__name__', '')
        if name:
            mod += '.' + name
        return mod

    def getTypeInspectURL(self):
        return dotted_name_url(self.getTypeName())

    def getViews(self, order=(0,2,1)):
        """Get all views for the context object.

        Return a list of three-tuples describing a view (<skinname>,
        <interface, <name>). The list is ordered by one of these
        categories. The order number is:

          0 for sort by skin
          1 for sort by interface
          2 for sort by name

        So, if the result should be sort in skin name order first,
        followed by interface name order, the order might be (0,1,2).
        """
        info = ViewInfo(self.context)
        view_list = list(info.getAllViews())
        return sorted(view_list,
                      key=lambda x: (x[order[0]], x[order[1]], x[order[2]]))

    def encode(self, text):
        text = str(text)
        text = text.replace(
            '&', '&amp;').replace(
            '<', '&lt;').replace(
            '>', '&gt;')
        return text
    
    def getYUIIncludes(self):
        # XXX: This is most probably the wrong approach
        needed = NeededInclusions()
        needed.need(yui.datatable)
        return needed.render()
