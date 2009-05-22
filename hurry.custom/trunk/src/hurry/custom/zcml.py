from zope.interface import Interface
from zope.schema import TextLine
from zope.configuration.fields import GlobalObject, Path

from hurry import custom

class ITemplateLanguage(Interface):
    template_class = GlobalObject(
        title=u'Template Class',
        description=u'The class that implements the template language')

    extension = TextLine(
        title=u'Extension',
        description=u'The filesystem extension (with period, '
                    u'for example .jsont) '
                    u'recognized for this template language')

    sample_extension = TextLine(
        title=u'Sample Extension',
        description=u'The filesystem extension used for sample input data.',
        required=False)

class IDataLanguage(Interface):
    parse_func = GlobalObject(
        title=u'Parse function',
        description=u'A function that can parse text and deliver input data.')

    extension = TextLine(
        title=u'Extension',
        description=u'The filesystem extension (with period, '
                    u'for example .json) '
                    u'recognzied for this input language')

class ICollection(Interface):
    id = TextLine(
        title=u'Collection ID',
        description=u"Globally unique collection id")

    path = Path(
        title=u"Path",
        description=u'Filesystem path to collection')

    title = TextLine(
        title=u"Title",
        description=u'Human-readable title for collection',
        required=False)

def action_template_language(_context,
                             template_class, extension, sample_extension=None):
    _context.action(
        discriminator = ('action_template_language',
                         template_class, extension, sample_extension),
        callable = custom.register_language,
        args = (template_class, extension, sample_extension))
    
def action_data_language(_context, parser_func, extension):
    _context.action(
        discriminator = ('action_data_language',
                         parser_func, extension),
        callable = custom.register_data_language,
        args = (parser_func, extension))
    
def action_collection(_context, id, path, title=None):
    _context.action(
        discriminator = ('action_collection', id),
        callable = custom.register_collection,
        args = (id, path, title))
