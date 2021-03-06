##parameters=password, confirm, domains=None, **kw
##title=Action to change password
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import Message as _

mtool = getToolByName(script, 'portal_membership')
rtool = getToolByName(script, 'portal_registration')

result = rtool.testPasswordValidity(password, confirm)
if result:
    return context.setStatus(False, result)

member = mtool.getAuthenticatedMember()
mtool.setPassword(password, domains)
if member.getProperty('last_login_time') == DateTime('1999/01/01'):
    member.setProperties(last_login_time='2000/01/01')

mtool.credentialsChanged(password)

return context.setStatus(True, _(u'Password changed.'))
