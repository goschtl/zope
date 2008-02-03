from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import ViewletBase, SearchBoxViewlet, PersonalBarViewlet

class FeatureViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/feature.pt')
    
    # def update(self):
    #     if IViewView.providedBy(self.__parent__):
    #         alsoProvides(self, IViewView)
        
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