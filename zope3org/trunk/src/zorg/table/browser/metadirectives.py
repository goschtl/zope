
from zope.interface import Interface
from zope.configuration.fields import GlobalObject,PythonIdentifier
from zope.configuration.fields import GlobalInterface,Tokens,Path,Bool
from zope.app.security.fields import Permission
from zope.app.component.fields import LayerField
from zope.schema import TextLine,Id,Bool, Choice
from zope.schema.vocabulary import SimpleVocabulary


class ICommonInformation(Interface):

    name = TextLine(
        title=u"Name",
        description=u"The name of the generated view.",
        required=True
        )

    for_ = GlobalInterface(
        title=u"Interface",
        description=u"""
        The interface this page (view) applies to.

        The view will be for all objects that implement this
        interface. The schema is used if the for attribute is not
        specified.

        If the for attribute is specified, then the objects views must
        implement or be adaptable to the schema.""",
        required=False
        )

    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=True
        )

    layer = LayerField(
        title=u"Layer",
        description=u"The later the view is in. Default: 'default'",
        required=False
        )

    template = Path(
        title=u"Template",
        description=u"An alternate template to use for the form.",
        required=False
        )

    class_ = GlobalObject(
        title=u"Class",
        description=u"""
        A class to provide custom widget definitions or methods to be
        used by a custom template.

        This class is used as a mix-in class. As a result, it needn't
        subclass any special classes, such as BrowserView.""",
        required=False
        )


class ITableViewDirective(ICommonInformation):
    
    config = TextLine(title=u'Default tableconfiguration',
                      required=True)


class ICellViewDirective(ICommonInformation):

    schema = GlobalInterface(
        title=u"Alternative Schema",
        description=u"""\
        If defined the cell view adapts its context to this schama to
        get the attribute of the content, by default it uses the
        schema of the cell""",
        required=False
        )
    
    field = TextLine(
        title=u"Alternative Fieldname",
        description=u"""\
        If defined the cell view uses this value to get the field of
        the schema to get the content value, by default the field
        defined in the cell is used.""",
        required=False
        )

    useForm = Bool(
        title=u"Use Form",
        description=u"""Use form to handle display and input.""",
        default=False,
        required=False)

    widget = GlobalObject(
        title=u"Widget Class",
        description=u"""The class that will create the widget.""",
        required=False)


class IRowViewDirective(ICommonInformation):
    pass


ACTION_DISPLAY_TOP = u"Top"
ACTION_DISPLAY_ROW = u"Row"
ACTION_DISPLAY_BOTTOM = u"Bottom"
    
class IActionViewDirective(ICommonInformation):

    useForm = Bool(
        title=u"Use Form",
        description=u"""Use form to handle input.""",
        default=True,
        required=False)
    
    display = Choice(
        title=u"Display",
        description=u"Select display position",
        vocabulary=SimpleVocabulary.fromItems(
        [(u"Top", ACTION_DISPLAY_TOP),
         (u"Row", ACTION_DISPLAY_ROW),
         (u"Bottom", ACTION_DISPLAY_BOTTOM)]),
        default=ACTION_DISPLAY_BOTTOM)


class IFilterViewDirective(ICommonInformation):
    pass
