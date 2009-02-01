from persistent import Persistent
from zope.app.container.contained import Contained
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.dublincore.annotatableadapter import partialAnnotatableAdapterFactory
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from zopesandbox.document.interfaces import IDocument

class Document(Contained, Persistent):

    implements(IDocument, IAttributeAnnotatable)
    
    title = FieldProperty(IDocument['title'])
    description = FieldProperty(IDocument['description'])
    body = FieldProperty(IDocument['body'])

# Custom dublin core adapter that reuses title and description,
# declared in the IDocument interface.
DocumentDublinCore = partialAnnotatableAdapterFactory(('title', 'description'))
