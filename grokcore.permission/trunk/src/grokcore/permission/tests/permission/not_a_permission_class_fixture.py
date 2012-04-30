import grokcore.component as grok
import grokcore.permission

class NotAPermissionSubclass(object):
    grok.name('not really a permission')

class MyRole(grokcore.permission.Role):
    grok.name('MyRole')
    grokcore.permission.permissions(NotAPermissionSubclass)
