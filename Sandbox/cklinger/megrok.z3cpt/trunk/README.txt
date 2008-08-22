megrok.z3cpt
============

This packages allows you to use z3c.pt in grok.Views.

Please note the extension for the template is *.3pt

Example 1:
----------

class Index(grok.View):
    grok.name('view')
    person=""

    def update(self):
        self.person="Christian"

index = megrok.z3cpt.z3cPageTemplate("""
                 <html xmlns="http://www.w3.org/1999/xhtml"
                       xmlns:tal="http://xml.zope.org/namespaces/tal">
                  <div>
                   Hello World!
                  </div>
                  <span tal:content="view.person" />
                 </html>
              """)

Example 2:
----------

class IndexFS(grok.View):
    pass # see app_templates/indexfs.3pt

$cat app_templates/indexfs.3pt 
<html xmlns="http://www.w3.org/1999/xhtml">
 <div>
    Hello World!
 </div>
</html>


