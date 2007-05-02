import os
import grok
from megrok import quarry

class QuarryDemo(grok.Application, grok.Container):
    pass


# access any template in the python path

class Index(quarry.View):
    quarry.template('megrok.quarry.demo.demoshare.template')






# skins and layers

class TestLayer(quarry.Layer):
    pass


class Test(quarry.Skin):
    grok.name('test') # default to this
    quarry.layer(TestLayer)
    # accessible as ++skin++test


class TestView(quarry.View):
    
    def render(self):
        return """<html><body><h1>GROK NO HIDE</h1>
        Now try http:://yourhost/++skin++test/yourdemo/@@hiddenview
        </body></html>"""






# viewlets

class MenuPage(quarry.View):
    quarry.template('megrok.quarry.demo.app.menu')
    grok.name('menu')

    title = "Viewlet Test Page"


class Menu(quarry.View):
    """ View class needed when defining inline page templates

    Due to a possible bug or implementation issue,
    the tal namespace 'provider' only seems to work with
    grok.PageTemplateFile and grok.PageTemplate or strings.
    """

menu = grok.PageTemplateFile(os.path.join('menu.pt'))



class MenuManager(quarry.ViewletManager):
    grok.context(MenuPage)
    grok.name('body') #talnamespace 'provider:body'


class Menu10(quarry.Viewlet):
    quarry.viewletmanager(MenuManager)

    def render(self):
        return "<li>Fish</li>"


class Menu20(quarry.Viewlet):
    quarry.viewletmanager(MenuManager)

    def render(self):
        return "<li>Stone Soup</li>"
    

class Menu30(quarry.Viewlet):
    """
    <li tal:repeat="item view/items">
      <span tal:replace="item" />
    </li>
    """
    quarry.viewletmanager(MenuManager)
    quarry.template('megrok.quarry.demo.app.Menu30.__doc__')
    
    def items(self): #accessible as view/items
        return ['Buffalo Wings', 'Celery', 'Blue Cheese' ,'Duffs T-shirt']

