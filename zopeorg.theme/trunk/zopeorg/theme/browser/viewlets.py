from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import ViewletBase, SearchBoxViewlet, PersonalBarViewlet

from plone.app.layout.globals.interfaces import IViewView 

class FeatureViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/feature.pt')
    
    def visible(self):
        # we should *climb up* to object itself from
        # 1. viewlet to viewletManager
        # 2. viewletManager to object
        if IViewView.providedBy(self.__parent__.__parent__):
            return True
        else:
            return False
        
    def tag(self, **kwargs):
        return self.context.getField('image').tag(self.context, **kwargs)
    
    def blurb(self):
        return self.context.getBlurb()
    
    def divider(self):
        return self.context.getDivider()  
    
class ZopeorgSearchBoxViewlet(SearchBoxViewlet):
    render = ViewPageTemplateFile('templates/searchbox.pt')
    
class ZopeorgPersonalBarViewlet(PersonalBarViewlet):
    render = ViewPageTemplateFile('templates/anonymous_personal_bar.pt')