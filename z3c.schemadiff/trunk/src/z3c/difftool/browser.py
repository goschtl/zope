from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from schema import diff

from difflib import HtmlDiff

class DiffView(object):
    template = PageTemplateFile('diff.pt')
    htmldiff = HtmlDiff(wrapcolumn=60)
    
    def __init__(self, source, target, request):
        self.source = source
        self.target = target
        self.request = request
    
    def __call__(self, *interfaces):
        results = diff(self.source, self.target, *interfaces)
        
        tables = [{'name': field.__name__,
                   'title': field.title,
                   'html': self.htmldiff.make_table(a, b, context=True)} for \
                  (field, (a, b)) in results.items()]

        return self.template(tables=tables)


