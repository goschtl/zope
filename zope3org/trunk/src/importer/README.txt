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

    >>> importer.download(url='file:src/importer/testsite/FrontPage')

The site must contain two files:

    >>> folder.get('FrontPage', None) is not None
    True
    
XXX this one is currently failing because recursion is not yet 
    implemented::
    
    >>> folder.get('ComponentArchitecture', None) is not None
    True

