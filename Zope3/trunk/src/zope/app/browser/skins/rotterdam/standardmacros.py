from zope.app.browser.skins.basic.standardmacros import StandardMacros

BaseMacros = StandardMacros

class StandardMacros(BaseMacros):
    __implements__ = BaseMacros.__implements__
    macro_pages = ('skin_macros', 'view_macros', 'dialog_macros')

