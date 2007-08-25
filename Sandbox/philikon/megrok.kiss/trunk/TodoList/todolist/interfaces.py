from zope import schema, interface

class ITodoItem(interface.Interface):

    title = schema.TextLine(title=u"Title")

    priority = schema.Choice(title=u'Category',
                             vocabulary='Todo Priorities')
