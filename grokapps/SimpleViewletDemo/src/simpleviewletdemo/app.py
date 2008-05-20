import grok
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema import TextLine

grok.context(Interface)

def get_application(context):
    obj = context
    while not isinstance(obj, App):
        obj = obj.__parent__
    return obj

class App(grok.Application, grok.Container):
    pass

class IFruit(Interface):
    name = TextLine(title=u"Name")

class Fruit(grok.Model):
    grok.implements(IFruit)

    def __init__(self, name):
        self.name = name

class Index(grok.View):
    grok.template('master')

class Head(grok.ViewletManager):
    grok.name('head')

class Title(grok.Viewlet):
    grok.viewletmanager(Head)

class AppCSS(grok.Viewlet):
    grok.viewletmanager(Head)
    grok.context(App)

class FruitCSS(grok.Viewlet):
    grok.viewletmanager(Head)
    grok.context(Fruit)

class Header(grok.ViewletManager):
    grok.name('header')

class Logo(grok.Viewlet):
    grok.viewletmanager(Header)
    grok.order(1)

class AdminBar(grok.Viewlet):
    grok.viewletmanager(Header)
    grok.order(2)

class Admin(grok.View):
    grok.template('master')

class LeftSidebar(grok.ViewletManager):
    grok.name('left')

class Navigation(grok.Viewlet):
    grok.viewletmanager(LeftSidebar)
    grok.order(1)

    def update(self):
        self.items = []

        rootfolder = get_application(self.context)
        for navitem in rootfolder.values():
            item = {'title': navitem.name,
                    'url': self.__parent__.url(obj=navitem) }
            self.items.append(item)

class Login(grok.Viewlet):
    grok.viewletmanager(LeftSidebar)
    grok.context(App)
    grok.view(Index)
    grok.order(2)

class MainArea(grok.ViewletManager):
    grok.name('main')

class Content(grok.Viewlet):
    grok.viewletmanager(MainArea)
    grok.context(App)
    grok.view(Index)

    def render(self):
        return '<div>Application object content area</div>'

class AddFruit(grok.Viewlet):
    grok.viewletmanager(MainArea)
    grok.context(App)
    grok.view(Admin)

    def update(self):
        self.form = getMultiAdapter((self.context, self.request),
                                    name='addfruitform')
        self.form.update_form()

    def render(self):
        return self.form.render()

class AddFruitForm(grok.AddForm):
    form_fields = grok.AutoFields(Fruit)

    @grok.action('Add fruit')
    def add(self, **data):
        obj = Fruit(**data)
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        app = get_application(self.context)
        self.redirect(self.url(obj=app))

class FruitContent(grok.Viewlet):
    grok.viewletmanager(MainArea)
    grok.context(Fruit)
    grok.template('fruit')

    def update(self):
        self.name = self.context.name

class Footer(grok.ViewletManager):
    grok.name('footer')

class Copyright(grok.Viewlet):
    grok.viewletmanager(Footer)
