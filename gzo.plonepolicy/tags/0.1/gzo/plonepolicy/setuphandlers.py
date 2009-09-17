from zope.component import getUtility
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import transaction
from Products.Five.utilities.interfaces import IMarkerInterfaces

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletType
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.app.portlets import portlets

from gzo.plonesmashtheme.portlets import grokdoc

def publicWebsiteLocation(context):
    "All Grok web site content lives in Folder at /public_website"
    # this makes it easier to manage content, especially if people
    # toss a lot of stuff in the top content level
    portal = context.getSite()
    if not base_hasattr(portal, 'public_website'):
        _createObjectByType(
            'Folder', portal, id='public_website',
            title='Grok',
            description=""
        )
    pubweb = portal['public_website']
    
    # mark public_website as INavigationRoot and publish it
    mifaces_for_pubweb = IMarkerInterfaces(pubweb)
    add = mifaces_for_pubweb.dottedToInterfaces(
        ['plone.app.layout.navigation.interfaces.INavigationRoot',]
    )
    mifaces_for_pubweb.update(add=add)
    wftool = getToolByName(portal, "portal_workflow")
    if wftool.getInfoFor(pubweb, 'review_state') != 'published':
        wftool.doActionFor(pubweb, 'publish')


def _get_column_portlet_data(name, context):
    # i wonder if a shortcut like this already exists?
    column_mgr  = getUtility(IPortletManager, name=name, context=context)
    return getMultiAdapter(
        (context, column_mgr,), IPortletAssignmentMapping, context=context)
    

def assignPortlets(context):
    "Portlet Assignment"

    if context.readDataFile('gzo.portlet_config.txt') is None:
        return
    
    portal = context.getSite()
    
    left = _get_column_portlet_data(u'plone.leftcolumn', portal)
    right = _get_column_portlet_data(u'plone.rightcolumn', portal)
    
    # delete stock portlets
    for key in left.keys():
        del left[key]
    for key in right.keys():
        del right[key]
    
    pubweb = portal.public_website
    left = _get_column_portlet_data(u'plone.leftcolumn', pubweb)
    
    if left.has_key('top'):
        return
    left[u'top'] = portlets.classic.Assignment('portlet_leftcolumntop','portlet')
    left[u'search'] = portlets.classic.Assignment('portlet_search','portlet')
    left[u'navigation'] = portlets.navigation.Assignment(
        includeTop=True, topLevel=0, )
    left[u'download'] = portlets.classic.Assignment('portlet_download','portlet')
    left[u'news'] = portlets.classic.Assignment('portlet_news','portlet')

    left.updateOrder(
        (u'top',u'search',u'navigation',u'news',u'download',)
    )


def configureGrokDocumentationHelpCenter(context):
    portal = context.getSite()
    pubweb = portal.public_website
    
    # PHC must already be installed at /public_website/documentation
    if not base_hasattr(pubweb, 'documentation'):
        return
    
    # TODO: shouldn't the HelpCenter provide ILocalPortletAssignable?
    mifaces_for_docs = IMarkerInterfaces(pubweb.documentation)
    add = mifaces_for_docs.dottedToInterfaces(
        ['plone.portlets.interfaces.ILocalPortletAssignable',]
    )
    mifaces_for_docs.update(add=add)

    # Assign Grok Doc portlet
    left = _get_column_portlet_data(u'plone.leftcolumn', pubweb.documentation)
    if not left.has_key('grokdoc'):
        left[u'grokdoc'] = grokdoc.Assignment()

    # Block parent portlets
    portletManager = getUtility(IPortletManager,
        name=u'plone.leftcolumn', context=pubweb.documentation)
    assignable = getMultiAdapter(
        (pubweb.documentation, portletManager,), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)


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
