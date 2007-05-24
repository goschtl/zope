import grok
from zope import interface
import os


class Template(grok.View):
    grok.context(interface.Interface)

template = grok.PageTemplate("""
<html><body>
<h2>GROK SMASH ZCML!</h2>
<ul>
<li><a href="./@@testview" tal:attributes="href python:view.url(context, '@@testview')">Test Skins & Layers</a></li>
<li><a href="./@@menu" tal:attributes="href python:view.url(context, '@@menu')">Viewlet Test Page</a></li>
</ul>
</body></html>
""")



class Master(grok.View):
    grok.context(interface.Interface)


master = grok.PageTemplateFile(os.path.join('master.pt'))

