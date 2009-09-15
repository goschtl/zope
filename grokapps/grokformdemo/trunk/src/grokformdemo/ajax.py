import grok
from hurry.jquery import jquery
from hurry.resource import Library, ResourceInclusion

class jsdir(grok.DirectoryResource):
    grok.name('js')
    grok.path('js')

localjs = Library('js')

tooltip = ResourceInclusion(localjs, 'jquery.tools.min.js', depends=[jquery])
mytooltip = ResourceInclusion(localjs, 'mytooltip.js', depends=[tooltip])

from zope.interface import Interface
from zope.security.proxy import removeSecurityProxy 

class InlineValidation(grok.JSON):
    grok.context(Interface)

    def validate(self, id, value):
        message=""
        field_id = id.split('-')[-1]
        context = removeSecurityProxy(self.context)
        field = context.fields.get(field_id)
        try:
            field.field.validate(value)
        except Exception, e:
            message = '<div class="fieldError"> <div class="error"> %s </div> </div>' %e.doc() 
        return {'id': id, 'message':message}    
