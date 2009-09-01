from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

class TopimageViewlet(ViewletBase):
    render = ViewPageTemplateFile('topimage.pt')
    
