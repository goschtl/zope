========
Importer
========

This package can be used to import legacy data from other sites. 
It's a simple wget reimplementation. It only follows internal links
at the same or deeper levels. Additionaly it does some 
prostprocessing.

    >>> from zope.app.folder import Folder
    >>> folder = Folder()

The importer can be retrieved by an adaption to IImporter:

    >>> from importer import IImporter
    >>> importer = IImporter(folder)

Import the site:

    >>> importer.download(url='file:src/importer/testsite/FrontPage',
    ...                   base_url='http://www.zope.org/Wikis/DevSite/'
    ...                            'Projects/ComponentArchitecture')

The test site contains three files (``Component`` beeing linked relatively):

    >>> folder.get('FrontPage', None) is not None
    True
    
    >>> folder.get('VisionStatement', None) is not None
    True
    
    >>> file = folder.get('Component', None)
    >>> file is not None
    True
