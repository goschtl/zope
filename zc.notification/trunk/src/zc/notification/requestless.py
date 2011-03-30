from zope.pagetemplate import pagetemplatefile, engine
from zope.app.pagetemplate import viewpagetemplatefile

class Context(engine.ZopeContextBase):
    def translate(self, msgid, domain=None, mapping=None, default=None):
        return i18n.translate(
            msgid, domain, mapping, context=self.principal, default=default)

class ZopeEngine(engine.ZopeEngine):
    _create_context = Context
    def getContext(self, __namespace=None, **namespace):
        if __namespace:
            if namespace:
                namespace.update(__namespace)
            else:
                namespace = __namespace

        context = self._create_context(self, namespace)

        # Put principal into context so path traversal can find it
        if 'principal' in namespace:
            context.principal = namespace['principal']

        # Put context into context so path traversal can find it
        if 'context' in namespace:
            context.context = namespace['context']

        return context

Engine = engine._TrustedEngine(ZopeEngine())

class AppPT(object):
    def pt_getEngine(self):
        return Engine

class PageTemplateFile(AppPT, pagetemplatefile.PageTemplateFile):

    def __init__(self, filename, _prefix=None):
        _prefix = self.get_path_from_prefix(_prefix)
        super(PageTemplateFile, self).__init__(filename, _prefix)

    def pt_getContext(self, instance, **_kw):
        # instance is object with 'context' and 'principal' atttributes.
        namespace = super(PageTemplateFile, self).pt_getContext(**_kw)
        namespace['view'] = instance
        namespace['context'] = context = instance.context
        return namespace

    def __call__(self, instance, *args, **keywords):
        namespace = self.pt_getContext(
            instance=instance, args=args, options=keywords)
        s = self.pt_render(
            namespace,
            showtal=getattr(instance, 'showTAL', 0),
            sourceAnnotations=getattr(instance, 'sourceAnnotations', 0),
            )
        return s

    def __get__(self, instance, type):
        return viewpagetemplatefile.BoundPageTemplate(self, instance)
