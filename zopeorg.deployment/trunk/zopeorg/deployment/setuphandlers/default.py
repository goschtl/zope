from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName

def importVarious(context):
    if context.readDataFile("zopeorg.deployment-default.txt") is None:
        return

    logger=context.getLogger("zopeorg.deployment")
    site=context.getSite()

    installRequiredProducts(logger, site)
    configurePortlets(logger, site)


def installRequiredProducts(logger, site):
    required=[
        "zopeorg.theme",
        "PloneFormGen",
    ]
    # Installation for these product is fully included in our GS profile,
    # so just mark them as installed.
    already_installed=[
    ]

    st=getToolByName(site, "portal_setup")
    # This works around a flaw in the GenericSetup API
    if not st.getImportContextID():
        st._import_context_id="profile-Products.CMFPlone:plone"

    qi=getToolByName(site, "portal_quickinstaller")
    for product in required:
        if not qi.isProductInstallable(product):
            logger.error("Product %s is required but is not installable" %
                    product)
        elif not qi.isProductInstalled(product):
            logger.info(qi.installProduct(product, locked=False))

    for product in already_installed:
        if not qi.isProductInstalled(product):
            qi.notifyInstalled(product, locked=False)


def configurePortlets(logger, site):
    rightColumn=getUtility(IPortletManager, name=u"plone.rightcolumn",
                            context=site)
    right=getMultiAdapter((site, rightColumn,), IPortletAssignmentMapping,
                            context=site)

    for portlet in [ u"news", u"events", u"calendar"]:
        if portlet in right:
            del right[portlet]




