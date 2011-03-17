# -*- coding: utf-8 -*-

try:
    import martian
    import grokcore.security
    from grokcore.view import components
    from cromlech.io.interfaces import IRenderer

    
    class ViewSecurityGrokker(martian.ClassGrokker):
        martian.component(components.View)
        martian.directive(grokcore.security.require, name='permission')

        def execute(self, factory, config, permission, **kw):
            for method_name in IRenderer:
                config.action(
                    discriminator=('protectName', factory, method_name),
                    callable=grokcore.security.util.protect_getattr,
                    args=(factory, method_name, permission),
                    )
            return True

except ImportError:
    pass
