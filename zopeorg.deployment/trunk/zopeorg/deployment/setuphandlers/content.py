from Products.CMFCore.utils import getToolByName

def importVarious(context):
    if context.readDataFile("zopeorg.deployment-content.txt") is None:
        return

    logger=context.getLogger("zopeorg.deployment")
    site=context.getSite()
    recatalog(context, logger)


def recatalog(context, logger):
    site=context.getSite()
    ct=getToolByName(site, "portal_catalog")
    ct.refreshCatalog()
    logger.info('Site re-catalogued.')

