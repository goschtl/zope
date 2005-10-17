========
Importer
========

This package can be used to import legacy data from other sites. 
It's a simple wget reimplementation. It only follows internal links
at the same or deeper levels. Additionaly it does some 
postprocessing.

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

Check the content of a the simplest document:

    >>> file.data
    '<html><head></head><body><h1>Component</h1><p>[...]</p></body></html>'

A selection of the metadata will be copied also:

    >>> from zope.app.dublincore.interfaces import IZopeDublinCore
    >>> from datetime import datetime
    
    >>> dc = IZopeDublinCore(file)
    >>> dc.title
    u'Component'
    >>> dc.format
    u'text/html'
    >>> dc.creators
    (u'http://www.zope.org/Members/Brian',)
    >>> dc.created
    datetime.datetime(2003, 8, 1, 0, 0, tzinfo=tzinfo(0))
    >>> dc.modified
    datetime.datetime(2003, 10, 10, 0, 0, tzinfo=tzinfo(0))
