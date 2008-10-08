import os
import zope.interface
import zope.schema
from z3c.csvvocabulary import CSVVocabulary

WhatVocabulary = CSVVocabulary(
    os.path.join(os.path.dirname(__file__), 'what-values.csv'))

class IHelloWorldMessage(zope.interface.Interface):
    """Information about a hello world message"""

    who = zope.schema.TextLine(
        title=u'Who',
        description=u'Name of the person sending the message',
        required=True)

    when = zope.schema.Date(
        title=u'When',
        description=u'Date of the message sent.',
        required=True)

    what = zope.schema.Choice(
        title=u'What',
        description=u'What type of message it is.',
        vocabulary=WhatVocabulary,
        default=u'cool',
        required=True)
