from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens,\
     PythonIdentifier, MessageID
from zope.schema import TextLine, Id

class IBasicViewInformation(Interface):
    """
    This is the basic information for all views.
    """

    for_ = Tokens(
        title=u"Specifications of the objects to be viewed",
        description=u"""This should be a list of interfaces or classes
        """,
        required=True,
        value_type=GlobalObject(missing_value=object())
        )

    class_ = GlobalObject(
        title=u"Class",
        description=u"A class that provides attributes used by the view.",
        required=False
        )

    layer = TextLine(
        title=u"The layer the view is in.",
        description=u"""
        A skin is composed of layers. It is common to put skin
        specific views in a layer named after the skin. If the 'layer'
        attribute is not supplied, it defaults to 'default'.""",
        required=False
        )

class IPagesDirective(IBasicViewInformation):
    """
    Define multiple pages without repeating all of the parameters.

    The pages directive allows multiple page views to be defined
    without repeating the 'for', 'permission', 'class', 'layer',
    'allowed_attributes', and 'allowed_interface' attributes.
    """

    for_ = GlobalObject(
        title=u"The interface this view is for.",
        required=False
        )

class IPagesPageSubdirective(Interface):
    """
    Subdirective to IPagesDirective
    """

    name = TextLine(
        title=u"The name of the page (view)",
        description=u"""
        The name shows up in URLs/paths. For example 'foo' or
        'foo.html'. This attribute is required unless you use the
        subdirective 'page' to create sub views. If you do not have
        sub pages, it is common to use an extension for the view name
        such as '.html'. If you do have sub pages and you want to
        provide a view name, you shouldn't use extensions.""",
        required=True
        )

    template = TextLine(
        title=u"The name of a page template.",
        description=u"""
        Refers to a file containing a page template (must end in
        extension '.pt').""",
        required=False
        )

    attribute = PythonIdentifier(
        title=u"The name of an attribute to publish.",
        description=u"""
        This is used to publish an attribute provided by a class,
        instead of a template.

        This is the attribute, usually a method, to be published as
        the page (view).  The default is "__call__".""",
        required=False
        )

    title = MessageID(
        title=u"The browser menu label for the page (view)",
        description=u"""
        This attribute must be supplied if a menu attribute is
        supplied.""",
        required=False
        )

class IPageDirective(IPagesDirective, IPagesPageSubdirective):
    """
    The page directive is used to create views that provide a single
    url or page.

    The page directive creates a new view class from a given template
    and/or class and registers it.
    """

class IImplementsDirective(Interface):
    """State that a class implements something.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

    interface = Tokens(
        title=u"One or more interfaces",
        required=True,
        value_type=GlobalObject()
        )

class IViewableDirective(Interface):
    """State that a class can be viewed.
    """
    class_ = GlobalObject(
        title=u"Class",
        required=True
        )

class ILayerDirective(Interface):
    """
    Register a layer
    """

    name = TextLine(
        title=u"Layer name",
        description=u"Layer name",
        required=True
        )

class ISkinDirective(Interface):
    """
    Register a skin
    """

    name = TextLine(
        title=u"Skin name",
        description=u"Skin name",
        required=True
        )

    layers = Tokens(
        title=u"The layers it consists of.",
        required=True,
        value_type=TextLine()
        )

class IDefaultSkinDirective(Interface):
    """
    Register a skin
    """

    name = TextLine(
        title=u"Default skin name",
        description=u"Default skin name",
        required=True
        )
