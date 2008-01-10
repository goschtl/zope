from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import ViewletBase, SearchBoxViewlet, PersonalBarViewlet

class FeatureViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/feature.pt')
    
    # def update(self):
    #     self.portal_state = getMultiAdapter((self.context, self.request),
    #                                         name=u'plone_portal_state')
    #     self.portal_url = self.portal_state.portal_url()
    #     url_tool = getToolByName(self.context, 'portal_url')
    #     contentPath = url_tool.getRelativeContentPath(self.context)
    #     
    #     if contentPath:
    #         self.section = 'default'
    #     else:
    #         self.section = contentPath[0]
    
class ZopeorgSearchBoxViewlet(SearchBoxViewlet):
    render = ViewPageTemplateFile('templates/searchbox.pt')
    
class ZopeorgPersonalBarViewlet(PersonalBarViewlet):
    render = ViewPageTemplateFile('templates/anonymous_personal_bar.pt')    
    
class ZopeorgHeaderDividerViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/divider.pt')    