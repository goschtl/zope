from zope.interface import Interface, Attribute

class IHurryCustomAPI(Interface):
    """API for hurry.custom.
    """
    def register_language(template_class, extension, sample_extension=None):
        """Register a template language with the system.

        template_class - a class which implements ITemplate
        extension - the filename extension to register this
                    language. (example: .jsont)
        sample_extension - the filename extension of sample data files
                           for an extension. (example: .json)
        """

    def register_data_language(parse_func, extension):
        """Register a data language for template input.

        parse_func - a function that takes a text and parses it into
                     a data structure.
        extension - the extension to register the data language under.
                     (example: .json).
        """
        
    def register_collection(id, path, title=None):
        """Register a collection of templates on the filesystem with the system.

        id - globally unique collection id (used to look up the collection)
        path - the path of the collection on the filesystem
        title - optionally, human-readable title for collection.
                By default the 'id' will be used.
        """

    def render(id, template_path, input):
        """Render a template.

        id - the id for the collection
        template_path - the relative path (or filename) of the template
                        itself, under the path of the collection
        input - input data for the template

        If the template raises a CompileError or RenderError, the
        system will automatically fall back on the original
        non-customized template.
        """
        
    def lookup(id, template_path):
        """Look up template.
        
        id - the id of the collection
        template_path - the relative path (or filename) of the template
                        itself, under the path of the collection
        """

    def collection(id):
        """Look up ITemplateDatabase for id.

        id - the id of the collection

        Will raise ComponentLookupError if no collection with this id exists.
        """

    def next_collection(id, db):
        """Look up the collection below this one.

        id - the id of the collection
        db - the db below which to look.

        Will raise ComponentLookupError if there is no db below this
        collection.

        Will also raise ComponentLookupError if no collection with this id exists.
        """

    def root_collection(id):
        """Look up the root collection.

        id - the id of the collection.

        Will raise ComponentLookupError if no collection with this id exists.
        """
        
    def check(id, template_path, source):
        """Test a template (before customization).

        id - the id for the collection
        template_path - the template path of the template being customized
        source - the source of the customized template

        This tries a test-compile of the template. If the
        compilation cannot proceed, a CompileError is raised.

        Then tries to render the template with any sample inputs.
        If a rendering fails, a RenderError is raised. In a special
        'data_id' attribute of the error the failing input data is
        indicated.

        If the check succeeds, no exception is raised.
        """
        
    def structure(id):
        """Get a list with all the templates in this collection.

        id - the collection id
        
        All recognized template extensions are reported; unrecognized
        extensions are ignored. Subdirectories are also reported.
    
        Returned is a list of all entries.
    
        List entries for templates look like this:
        
        { 'template': 'template1.st',
        'name': 'template1',
        'extension': '.st'
        'path': 'template1.st',
        }

        template: the name of the template as it is in its immediate
                  directory.
        name: the name of the template without extension
        extension: the template extension
        path: the relative path to the extension from the collection_path
    
        List entries for sub directories look like this:
    
        { 'directory': 'subdirname',
        'entries': [ ... ],
        'path': 'subdirname',
        }

        directory: the name of the directory
        entries: the entries of the subdirectory, in a list
        path: the relative path to this directory from the collection_path
        """

    def recognized_languages():
        """Get an iterable with the recognized languages.
        
        The items are name-value pairs (language extension, template class).
        """
    
class ITemplate(Interface):
    """Uses for classes implementing a template language.

    When creating an object that provides ITemplate, raise
    a CompileError if the template text cannot be processed.
    """
    source = Attribute("The source text of the template.")

    def __call__(input):
        """Render the template given input.

        input - opaque template-language native data structure.

        Raise a RenderError if the template cannot be rendered.
        """

class CompileError(Exception):
    """Error when a template is broken (cannot be parsed/compiled).
    """

class RenderError(Exception):
    """Error when an error cannot be rendered (incorrect input data or
    other run-time error.
    """

class IDataLanguage(Interface):
    def __call__(data):
        """Parse data into data structure that can be passed to ITemplate()"""

class ISampleExtension(Interface):
    """Marker interface used to register the extension of the sample language.
    """

class IManagedTemplate(ITemplate):
    template = Attribute("The real template object being managed.")

    def check():
        """Update the template if it has changed.
        """

    def load():
        """Load the template from the filesystem.
        """

class NotSupported(Exception):
    pass

class ITemplateDatabase(Interface):
    """A per-collection template database.
    """
    id = Attribute("The id of the collection")
    title = Attribute("The title of the collection")

    def update(template_id, source):
        """Update the source for a given template.

        Updates the source and modification time for the template with
        that id.

        If this operation is not supported, a NotSupported error is
        raised.
        """

    def get_source(template_id):
        """Get the source of a given template.

        Returns None if the source cannot be loaded.
        """

    def get_modification_time(template_id):
        """Get the time at which a template was last updated.

        Time must be in number of seconds since epoch (preferably with
        sub-second accuracy, but this is database dependent).

        Returns None if the time cannot be retrieved.
        """
        
    def get_samples(template_id):
        """Get samples for a given template.

        Returns a dictionary with sample inputs.

        keys are the unique ids for the sample inputs.
        values are the actual template-language native data structures.
        """
