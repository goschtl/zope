from zope.component import getUtility
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import transaction

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletType

from plone.app.portlets import portlets

def assignPortlets(context):
    "Portlet Assignment"

    if context.readDataFile('gzo.portlet_config.txt') is None:
        return
    
    portal = context.getSite()
    
    leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)

    left = getMultiAdapter((portal, leftColumn,), IPortletAssignmentMapping, context=portal)
    right = getMultiAdapter((portal, rightColumn,), IPortletAssignmentMapping, context=portal)
    
    # delete stock portlets
    for key in left.keys():
        del left[key]
    for key in right.keys():
        del right[key]
    
    left[u'top'] = portlets.classic.Assignment('portlet_leftcolumntop','portlet')
    left[u'search'] = portlets.classic.Assignment('portlet_search','portlet')
    left[u'navigation'] = portlets.navigation.Assignment(
        includeTop=True, topLevel=0, )
    left[u'news'] = portlets.classic.Assignment('portlet_news','portlet')
    left[u'download'] = portlets.classic.Assignment('portlet_download','portlet')

    left.updateOrder(
        (u'top',u'search',u'navigation',u'news',u'download',)
    )

def removeDefaultContent(context):
    # TODO: if we load the sample content front-page we get "potential link breakage"
    # warnings and things don't work ...
    plone = context.getSite()
    try:
        plone.manage_delObjects('front-page')
        transaction.commit()
    except AttributeError:
        # already deleted
        pass

def _createLorumIpsumNews(p):
    "Some dummy news for CSS styling"
    _createObjectByType(
        'News Item', p['news'], id='gzo-relaunch',
        title='grok.zope.org to relaunch',
        description="""
        The Grok Neanderthal Sprint in Cologne is providing the community
        with a new CMS based web site. There is the new Plone 3 release
        under the hood."""
    )
    _createObjectByType(
        'News Item', p['news'], id='sample-one',
        title='some boring sample news',
        description="As if all news could be this interesting."
    )
    _createObjectByType(
        'News Item', p['news'], id='sample-two',
        title='more sample news',
        description="Thats the best news I heard all day."
    )
    wftool = getToolByName(p, "portal_workflow")
    for c in ['gzo-relaunch','sample-one','sample-two',]:
        content = p['news'][c]
        if wftool.getInfoFor(content, 'review_state') != 'published':
            wftool.doActionFor(content, 'publish')

def setupSampleContent(context):
    "Sample content for providing something to add CSS too"
    if context.readDataFile('gzo.sample_content.txt') is None:
        return
    
    # p is for plone site
    p = context.getSite()
    existing = p.objectIds()
    wftool = getToolByName(p, "portal_workflow")

    contents = ['front-page','sample-page', 'about', 'contribute', 'develop', 'download']
    for c in contents:
        if base_hasattr(p, c):
            content = p[c]
            if wftool.getInfoFor(content, 'review_state') != 'published':
                wftool.doActionFor(content, 'publish')
    
    # toss in some sample news items and publish them
    if not base_hasattr(p['news'], 'gzo-relaunch'):
        _createLorumIpsumNews(p)
