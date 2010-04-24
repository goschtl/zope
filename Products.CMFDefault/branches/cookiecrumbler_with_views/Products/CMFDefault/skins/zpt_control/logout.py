## Script (Python) "logout"
##title=Logout handler
##parameters=
from Products.CMFCore.utils import getToolByName

cctool = getToolByName(context, 'cookie_authentication')
stool = getToolByName(context, 'portal_skins')
utool = getToolByName(context, 'portal_url')
REQUEST = context.REQUEST

stool.clearSkinCookie()
cctool.logout(REQUEST.RESPONSE)
return REQUEST.RESPONSE.redirect(utool() + '/logged_out')