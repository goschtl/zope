from zope.interface import Interface, Attribute

class IHurryCustomAPI(Interface):
    """API for hurry.custom.
    """
    def register_language(template_class):
        """Register a template language with the system.

        The template language is a class which implements ITemplate
        """

    def register_collection(id, path, title=None):
        """Register a collection of templates on the filesystem with the system.

        id - globally unique collection id (used to look up the collection)
        path - the path of the collection on the filesystem
        title - optionally, human-readable title for collection.
                By default the 'id' will be used.
        """
    
    def lookup(id, template_path):
        """Look up template.
        
        id: the id for the collection
        template_path: the relative path (or filename) of the template
                       itself, under the path of the collection
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
    source = Attribute("The source text of the template.")

    def __call__(input):
        """Render the template given input.

        input - opaque template-language native data structure.
        """
        
class IDataLanguage(Interface):
    def __call__(data):
        """Parse data into data structure that can be passed to ITemplate()"""

class ISampleExtension(Interface):
    """Marker interface used to register the extension of the sample language.
    """

class IManagedTemplate(ITemplate):

    template = Attribute("The real template object being managed.")

    original_source = Attribute("The original source of the template, "
                                "before customization.")

    def check():
        """Update the template if it has changed.
        """

    def load():
        """Load the template from the filesystem.
        """
    
    def samples():
        """Get samples.

        Returns a dictionary with sample inputs.

        keys are the unique ids for the sample inputs.
        values are the actual template-language native data structures.
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

