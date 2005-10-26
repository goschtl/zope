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

    >>> from zorg.importer import IImporter
    >>> importer = IImporter(folder)

Import the site:

    >>> importer.download(url=download_url,
    ...                   target_url='http://localhost/site',
    ...                   base_url='http://www.zope.org/Wikis/DevSite/'
    ...                            'Projects/ComponentArchitecture')

The test site contains three wiki pages (``Component`` beeing linked relatively):

    >>> sorted(folder.keys())
    [u'Component', u'FrontPage', u'VisionStatement']
    
Each page is converted into a folder with an ``index.html`` document:

    >>> file = folder[u'Component'][u'index.html']

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
