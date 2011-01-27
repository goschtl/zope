#

import grokcore.view as grok

class BaseView(grok.View):
    grok.template('view')
    grok.context(object)

