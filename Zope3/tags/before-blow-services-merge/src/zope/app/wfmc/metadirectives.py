"""ZCML directives for defining privileges.

$Id: $
"""

import zope.interface
import zope.schema
import zope.configuration.fields

class IdefineXpdl(zope.interface.Interface):

    file = zope.configuration.fields.Path(
        title=u"File Name",
        description=u"The name of the xpdl file to read.",
        )

    process = zope.schema.TextLine(
        title=u"Process Name",
        description=u"The name of the process to read.",
        )

    id = zope.schema.Id(
        title=u"ID",
        description=(u"The identifier to use for the process.  "
                     u"Defaults to the process name."),
        )
