from zope.publisher.browser import BrowserView
from zope.app.interfaces.container import IReadContainer
from zope.app.traversing import objectName, getParents
from zope.component import queryView

class XmlObjectView(BrowserView):
    """Provide a xml interface for dynamic navigation tree in UI"""

    __used_for__ = IReadContainer

    def children_utility(self):
        """Return an XML document that contains the children of an object."""
        result = []
        container = self.context
        for name in container.keys():
            item = container[name]
            icon = queryView(item, 'zmi_icon', self.request)
            if IReadContainer.isImplementedBy(item):
                result.append(
                    '<collection name="%s" length="%s" icon_url="%s"/>'
                    % (name, len(item), icon.url()))
            else:
                result.append(
                    '<item name="%s" icon_url="%s"/>'
                    % (name, icon.url()))
        return ' '.join(result)

        
    def children(self):
        """ """
        self.request.response.setHeader('Content-Type', 'text/xml')
        return (u'<?xml version="1.0" ?><children> %s </children>'
                % self.children_utility()
                )

    def singleBranchTree(self, root=''):
        """Return an XML document with the siblings and parents of an object.
        
        There is only one branch expanded, in other words, the tree is
        filled with the object, its siblings and its parents with
        their respective siblings.

        """
        result = ''
        oldItem = self.context
        for item in getParents(self.context):
            # skip skin if present
            if item == oldItem:
                    continue
            subItems = []
            for name in item.keys():
                subItem = item[name]
                icon = queryView(subItem, 'zmi_icon', self.request)
                if IReadContainer.isImplementedBy(subItem):
                    if oldItem and subItem == oldItem:
                        subItems.append(
                            '<collection name="%s" length="%s" '
                            'icon_url="%s">%s</collection>'
                            % (name, len(subItem), icon.url(), result)
                            )
                    else:
                        subItems.append(
                            '<collection name="%s" length="%s" '
                            'icon_url="%s"/>'
                            % (name, len(subItem), icon.url())
                            )
                else:
                    subItems.append('<item name="%s" />' % name)

            result = ' '.join(subItems)
            oldItem = item

        # do not forget root folder
        icon = queryView(oldItem, 'zmi_icon', self.request)
        result = ('<collection name="%s" length="%s" icon_url="%s" '
                  'isroot="">%s</collection>'
                  % ('', len(oldItem), icon.url(), result)
                  )
        
        self.request.response.setHeader('Content-Type', 'text/xml')
        return u'<?xml version="1.0" ?><children> %s </children>' % result
