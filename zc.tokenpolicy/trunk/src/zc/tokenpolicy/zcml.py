from zope import interface, schema
import zope.configuration.fields
from zc.tokenpolicy import policy

class IPrivileges(interface.Interface):

    titles = zope.configuration.fields.Tokens(
        title=u"Privileges",
        description=u"List of privilege titles",
        value_type=schema.TextLine(),
        )

def Privileges(_context, titles):

    _context.action(
        discriminator='zc:tokenPrivileges',
        callable=policy.definePrivilegesByTitle,
        args=(titles,),
        )
