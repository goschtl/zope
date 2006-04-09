# Make a pacakge.



from zope.app.basicskin.standardmacros import StandardMacros as BaseMacros

class StandardMacros(BaseMacros):
    macro_pages = ('skin_macros', 'view_macros', 'dialog_macros'
                  , 'navigation_macros')
