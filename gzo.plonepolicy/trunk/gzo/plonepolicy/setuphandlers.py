from zope.component import getUtility
from zope.component import getMultiAdapter

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
        # keep navigation
        if key == u'navigation':
            continue
        del left[key]
    for key in right.keys():
        del right[key]
    
    left[u'top'] = portlets.classic.Assignment('portlet_leftcolumntop','portlet')
    left[u'news'] = portlets.classic.Assignment('portlet_news','portlet')
    left[u'download'] = portlets.classic.Assignment('portlet_download','portlet')

