import zope
import interfaces

class Unspecified: pass

def getAttribute(item, attribute, default=Unspecified):
        for attribute in attribute.split('.'):
            if hasattr(item, attribute) \
            or (hasattr(item, 'has_key') and item.has_key(attribute)) \
            or default is Unspecified:
                if hasattr(item, 'has_key'):
                    item = item[attribute]
                else:
                    item = getattr(item, attribute)
            else:
                return default
        return item

class Column:
    zope.interface.implements(interfaces.IColumn)

    def __init__(self, title):
        self.title = title

    def renderHeader(self, formatter):
        return self.title 

    def renderCell(self, item, formatter):
        return item

    def getSortKey(self, item, formatter):
        return None


class AttributeColumn(Column):
    zope.interface.implements(interfaces.IColumn)

    def __init__(self, title, attribute, default=Unspecified):
        self.title = title
        self.attribute = attribute
        self.default = default

        self.sortable = False

    def renderCell(self, item, formatter):
        return getAttribute(item, self.attribute)
