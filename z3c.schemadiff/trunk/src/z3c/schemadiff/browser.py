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

        tables = []
        for field, result in results.items():
            try:
                a, b = result
            except ValueError:
                html = result
            else:
                html = self.htmldiff.make_table(a, b, context=True)

            tables.append({
                'name': field.__name__,
                'title': field.title,
                'html': html})

        return self.template(tables=tables)


