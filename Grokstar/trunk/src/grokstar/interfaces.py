from zope.interface import Interface
from zope import schema, interface
from zope.app.container.interfaces import IContainer

CREATED = 0
PUBLISHED = 1
class IBlog(Interface):
    title = schema.TextLine(title=u'Title')
    tagline = schema.TextLine(title=u'Tagline')
    footer = schema.TextLine(title=u'Footer', required=False)
    email = schema.TextLine(title=u'Email')

class IEntry(IContainer):
    """
    This interface is based on the Atom entry definition, from the Atom RFC.
    
    http://tools.ietf.org/html/rfc4287
    """
    
    # id is generated when we generate entry text
    
    title = schema.TextLine(title=u"Title", required=True)

    updated = schema.Datetime(title=u"Updated", required=True)

    published = schema.Datetime(title=u"Published", required=False)

##     authors = schema.List(title=u"Authors", value_type=schema.Object,
##                           default=[])

##     contributors = schema.List(title=u"Contributors", value_type=schema.Object,
##                                default=[])

    categories = schema.List(title=u"Categories",
                             value_type=schema.TextLine(title=u"Categories"),
                             default=[])
 
    #links = schema.List(title=u"Links", value_type=schema.TextLine,
    #                    default=[])

    summary = schema.SourceText(title=u"Summary", required=False)

    content = schema.SourceText(title=u"Content")

    # rightsinfo = schema.SourceText(title=u"Rights", required=False)

    # source is too complicated to support for us right now

class IRestructuredTextEntry(IEntry):
    content = schema.SourceText(title=u"Content")
    
class IComment(Interface):
    date = schema.Datetime(title=u"Date", required=True)
    
    comment = schema.SourceText(title=u"Comment", required=True)
    
    author = schema.TextLine(title=u"Author", required=True)

class IAtomEntry(Interface):
    
    def xml():
        """Return Atom representation of an entry.
        """

class IAtomContent(Interface):
    def xml():
        """Return Atom representation of content of object.
        """
        
