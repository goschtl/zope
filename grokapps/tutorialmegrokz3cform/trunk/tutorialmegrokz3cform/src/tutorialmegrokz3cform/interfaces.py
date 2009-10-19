import os
import zope.interface
import zope.schema

class IContact(zope.interface.Interface):
    """A z3c.form contact form."""

    name = zope.schema.TextLine(
        title=u'Name',
        description=u'Name of the person.',
        required=True)

    description = zope.schema.TextLine(
        title=u'Description',
        description=u'Description of the person',
        required=True)
