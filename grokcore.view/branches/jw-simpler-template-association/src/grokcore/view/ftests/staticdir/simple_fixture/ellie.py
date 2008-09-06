import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class Index(grok.View):
    grok.template('index')
