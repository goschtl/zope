import zope.interface
import grokcore.view
import grokcore.component
import fanstatic

lib = fanstatic.Library('grokcore.resource.tests', 'resources')

css_a = fanstatic.Resource(lib, 'a.css')
css_b = fanstatic.Resource(lib, 'b.css')
css_c = fanstatic.Resource(lib, 'c.css')
css_d = fanstatic.Resource(lib, 'd.css')

grokcore.view.templatedir('templates')

class IMySuperIface(zope.interface.Interface):
    pass

class MyView(grokcore.view.View):
    grokcore.component.context(zope.interface.Interface)
    grokcore.resource.include(css_a)
    grokcore.view.template('index')

class ViewWithExtraResource(MyView):
    grokcore.resource.include(css_b)

class ViewWithMultipleResources(grokcore.view.View):
    grokcore.component.context(zope.interface.Interface)
    grokcore.resource.include(css_c, css_b)
    grokcore.view.template('index')

class ViewWithMultipleResourceCalls(grokcore.view.View):
    grokcore.component.context(zope.interface.Interface)
    grokcore.resource.include(css_c, css_b)
    grokcore.resource.include(css_a)
    grokcore.view.template('index')

class ViewWithResourceInUpdate(grokcore.view.View):
    grokcore.component.context(zope.interface.Interface)
    grokcore.resource.include(css_a)
    grokcore.view.template('index')

    def update(self):
        css_d.need()

class MySuperView(grokcore.view.View):
    grokcore.component.context(zope.interface.Interface)
    zope.interface.implements(IMySuperIface)
    grokcore.view.template('index')

class MySuperViewWithResource(grokcore.view.View):
    grokcore.component.context(zope.interface.Interface)
    zope.interface.implements(IMySuperIface)
    grokcore.resource.include(css_a)
    grokcore.view.template('index')
