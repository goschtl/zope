from zope.publisher.browser import BrowserView
from zope.app.interfaces.container import IReadContainer
from zope.app.traversing import objectName, getParents, getParent
from zope.component import queryView
from zope.interface import Interface


class ReadContainerXmlObjectView(BrowserView):
    """Provide a xml interface for dynamic navigation tree in UI"""

    __used_for__ = IReadContainer

    def getIconUrl(self, item):
        result = ''
        icon = queryView(item, 'zmi_icon', self.request) 
        if icon:
            result = icon.url()
        return result

    def children_utility(self):
        """Return an XML document that contains the children of an object."""
        result = []
        container = self.context
        for name in container.keys():
            item = container[name]
            iconUrl = self.getIconUrl(item)
            if IReadContainer.isImplementedBy(item):
                result.append(
                    '<collection name="%s" length="%s" icon_url="%s"/>'
                    % (name, len(item), iconUrl))
            else:
                result.append(
                    '<item name="%s" icon_url="%s"/>'
                    % (name, iconUrl))
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
                iconUrl = self.getIconUrl(subItem)
                if IReadContainer.isImplementedBy(subItem):
                    if oldItem and subItem == oldItem:
                        subItems.append(
                            '<collection name="%s" length="%s" '
                            'icon_url="%s">%s</collection>'
                            % (name, len(subItem), iconUrl, result)
                            )
                    else:
                        subItems.append(
                            '<collection name="%s" length="%s" '
                            'icon_url="%s"/>'
                            % (name, len(subItem), iconUrl)
                            )
                else:
                    subItems.append('<item name="%s" />' % name)

            result = ' '.join(subItems)
            oldItem = item

        # do not forget root folder
        iconUrl = self.getIconUrl(oldItem)
        result = ('<collection name="%s" length="%s" icon_url="%s" '
                  'isroot="">%s</collection>'
                  % ('', len(oldItem), iconUrl, result)
                  )
        
        self.request.response.setHeader('Content-Type', 'text/xml')
        return u'<?xml version="1.0" ?><children> %s </children>' % result
 
class XmlObjectView(BrowserView):
    """Provide a xml interface for dynamic navigation tree in UI"""

    __used_for__ = Interface


    def singleBranchTree(self, root=''):
        parent = getParent(self.context)
        while parent:
                if IReadContainer.isImplementedBy(parent):
                        container = parent
                        view = queryView(container, 'singleBranchTree.xml', self.request)
                        return view()
                else:
                    parent = getParent(parent)

