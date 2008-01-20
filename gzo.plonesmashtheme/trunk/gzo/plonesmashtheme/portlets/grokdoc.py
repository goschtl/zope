from zope.interface import implements
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_quote_plus

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.portlets.cache import render_cachekey
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress


class IGrokDocPortlet(IPortletDataProvider):
    "PHC Documentation Portlet By Topic"
    # This portlet should probably be in PHC and then we just provide
    # a custom template?

class Assignment(base.Assignment):
    implements(IGrokDocPortlet)

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('phc_grok.pt')

    # TODO: chucks an error?
    #@ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    # duplicate of Products.PloneHelpCenter.browser.helpcenter.HelpCenterView.getSectionMap
    def getSectionMap(self):
        """
          returns a complex list of section dicts
          [{title:sectiontitle, subtopics:listOfSubTopics, url:urlOfSection, count:itemsInSection}, ...]
          subtopics are each lists [{title:titleOfSubSection,url:urlOfSubSection}]
          This is used in helpcenter_ploneorg.pt.
        """

        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        phc = context.getPHCObject()
        here_url = phc.absolute_url()
        
        topics = phc.getSectionsVocab()

        # dict to save counts
        topicsDict = {}

        for topic in topics:
            if ':' not in topic:
                items = catalog(portal_type=['HelpCenterReferenceManual','HelpCenterTutorial','HelpCenterHowTo'],
                                               review_state='published',
                                               getSections=[topic])
                for item in items:
                    for section in item.getSections:
                        topicsDict[section] = topicsDict.get(section, 0) + 1

        sections = []
        currTitle = ''
        for topic in topics:
            count = topicsDict.get(topic)
            if count:
                # break into main topic, sub topic
                cs = [s.strip() for s in topic.split(':')]
                main = cs[0]
                sub = ': '.join(cs[1:])

                if main != currTitle:
                    # append a new topic dict
                    currTitle = main
                    currSubSections = []
                    sections.append(
                     {'title':currTitle,
                      'subtopics':currSubSections,
                      'url': here_url + '/phc_topic_area?topic=' + url_quote_plus(currTitle),
                      'count':count
                      }
                     )
                if sub:
                    # add to the subtopics list
                    id = sub.lower().replace(' ','-')  # make HTML anchor ID
                    currSubSections.append(
                     {'title':sub,
                      'url': "%s/phc_topic_area?topic=%s#%s" % (here_url, url_quote_plus(currTitle), id)
                      }
                     )

        return sections

class AddForm(base.AddForm):
    form_fields = form.Fields(IGrokDocPortlet)
    label = _(u"Add Grok Doc Portlet")
    description = _(u"This portlet displays Help Center content by Topic.")

    def create(self, data):
        return Assignment()

class EditForm(base.EditForm):
    form_fields = form.Fields(IGrokDocPortlet)
    label = _(u"Edit Grok Doc Portlet")
    description = _(u"This portlet displays Help Center content by Topic.")
