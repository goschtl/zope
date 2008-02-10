import  zope.interface
import  zope.schema

import grok

from tfws.website import interfaces

class FolderIndexForContent(grok.Adapter):
    """Adapt possible folder to folder.
    """
    grok.context(interfaces.IContent)
    grok.provides(interfaces.IIndexFolder)

    def __init__(self, context):
        self.context = context

    def setFolderIndex(self, item=None):
        # remove any current index
        for page in self.context.values():
            if interfaces.IFolderIndex.providedBy(page):
                zope.interface.directlyProvides(page, 
                    zope.interface.directlyProvidedBy(page) - \
                                         interfaces.IFolderIndex)
        # set the index page
        if item is not None:
            zope.interface.directlyProvides(item, 
                    interfaces.IFolderIndex, 
                    zope.interface.directlyProvidedBy(item))

class FolderIndexSource(object):
    """A source of items in a folder."""

    def __call__(self, context):

        result = []
        for key in context.values():
            item = context[key]
            term = zope.schema.vocabulary.SimpleTerm(item, token=item.title)
            result.append(term)
        return zope.schema.vocabulary.SimpleVocabulary(result)

grok.global_utility(FolderIndexSource, 
                    provides=zope.schema.interfaces.IVocabularyFactory,
                    name=u'Folder Index Source')


@grok.subscribe(interfaces.IPage, grok.IObjectCopiedEvent)
def removeFolderIndexOnCopiedObject(item, event):
    """Remove IFolderIndex on copied objects.
    
    This handler removes the IFolderIndex from a copied object after
    copy/paste. This is needed for clean up copied objects because we can't have
    more the one object marked with IFolderIndex.

    """
    if interfaces.IFolderIndex.providedBy(item):
            zope.interface.directlyProvides(item, 
            zope.interface.directlyProvidedBy(item) - interfaces.IFolderIndex)
