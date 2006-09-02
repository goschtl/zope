from zope import interface
from zope import schema

from z3c.sampledata import _


class ISampleManagerDirective(interface.Interface):
    """Parameters for the sample manager."""

    name = schema.TextLine(
            title = _(u"Name"),
            description = _(u'The unique name of the sample manager'),
            )

    seed = schema.TextLine(
            title = _(u'Seed'),
            description = _(u'The seed for the random generator'),
            required = False,
            default = u''
            )


class IGeneratorSubDirective(interface.Interface):
    """Parameters for the 'generator' subdirective."""

    name = schema.TextLine(
            title = _(u"Name"),
            description = _(u'The unique name of the sample manager'),
            )

    dependsOn = schema.TextLine(
            title = _(u"Dependencies"),
            description = _(u'The generators this generator depends on.\n'
                            u'As space separated list.'),
            default = u'',
            required = False,
            )

    contextFrom = schema.TextLine(
            title = _(u"Context from"),
            description = _(u'Context for the generator is taken from this'
                            u' generator.'),
            default = u'',
            required = False,
            )

