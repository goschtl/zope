import grokcore.component as grok


from grokcore.registries.tests.registries.interfaces import IExample


class MyExample(grok.GlobalUtility):
    grok.name('global')
    grok.implements(IExample)
