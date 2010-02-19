import grok

from zope.interface import Interface
from megrok.reload.code import reload_code
from megrok.reload.interfaces import IReload
from megrok.reload.zcml import reload_zcml

grok.templatedir('templates')

class Reload(grok.View):
    """Reload view.
    """
    grok.context(Interface)
    grok.implements(IReload)
    message = None

    def update(self):
        action = self.request.form.get('action')
        if action is not None:
            if action == 'code':
                self.message = self.code_reload()
            elif action == 'zcml':
                self.message = self.zcml_reload()

    def status(self):
        return self.message

    def code_reload(self):
        reloaded = reload_code()

        result = ''
        if reloaded:
            result += 'Code reloaded:\n\n'
            result += '\n'.join(reloaded)
        else:
            result = 'No code reloaded!'
        return result

    def zcml_reload(self):

        # We always do an implicit code reload so we can register all newly
        # added classes.
        reloaded = reload_code()
        reload_zcml()

        # TODO Minimize all caches, we only really want to invalidate the
        # local site manager from all caches
        # aq_base(self.context)._p_jar.db().cacheMinimize() BBB
        result = ''
        if reloaded:
            result += 'Code reloaded:\n\n'
            result += '\n'.join(reloaded)
        else:
            result = 'No code reloaded!'
        result += '\n\nGlobal ZCML reloaded.'
        return result
