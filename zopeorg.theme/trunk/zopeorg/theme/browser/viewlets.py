from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets.common import SearchBoxViewlet, PersonalBarViewlet      
    
class ZopeorgSearchBoxViewlet(SearchBoxViewlet):
    render = ViewPageTemplateFile('templates/searchbox.pt')
    
class ZopeorgPersonalBarViewlet(PersonalBarViewlet):
    render = ViewPageTemplateFile('templates/anonymous_personal_bar.pt')        