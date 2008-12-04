import grok
from z3c.objpath.path import resolve, path

from hurry import resource
from hurry import yui
from hurry.explorer import explorer

explorertests_lib = resource.Library('explorertests')

explorertests = resource.ResourceInclusion(
    explorertests_lib,
    'testexplorer.js',
    depends=[explorer, yui.logger, yui.yuitest],
    bottom=True,
    )

class TestContainer(grok.Container):
    pass

class JsTestApp(TestContainer, grok.Application):
    pass

@grok.subscribe(JsTestApp, grok.IObjectAddedEvent)
def add(obj, event):
    obj['a'] = TestContainer()
    obj['b'] = TestContainer()
    obj['a']['c'] = TestContainer()
    obj['a']['d'] = TestContainer()
    obj['b']['e'] = TestContainer()
    obj['b']['f'] = TestContainer()
    obj['a']['c']['g'] = TestContainer()
    obj['a']['c']['h'] = TestContainer()
    
class ExplorerInfo(grok.JSON):
    grok.context(TestContainer)

    def treeinfo(self):
        container = self._container()
        nodes = []
        for obj in container.values():
            if not isinstance(obj, TestContainer):
                continue
            nodes.append(
                {'label': obj.__name__,
                 'path': path(grok.getSite(), obj)})
        return { 'nodes': nodes }
        
    def tableinfo(self):
        container = self._container()
        result = []
        for key, value in container.items():
            title = key
            container = isinstance(value, TestContainer)
            result.append({'name': key,
                           'title': title,
                           'path': path(grok.getSite(), value),
                           'container': container})
        return {'records' : result }

    def _container(self):
        return resolve(grok.getSite(), self.request.form['nodepath'])

class TabInfo(grok.View):
    grok.context(TestContainer)

    def update(self):
        self.container = resolve(grok.getSite(), self.request.form['nodepath'])
    
class Index(grok.View):
    grok.context(TestContainer)

    def update(self):
        resource.bottom()
        
        yui.reset.need()
        yui.fonts.need()
        yui.grids.need()
        yui.sam.need()
        explorertests.need()
