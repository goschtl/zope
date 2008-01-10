
def importVarious(context):
    logger=context.getLogger("zopeorg.deployment")
    site=context.getSite()
    recatalog(context, logger)


def recatalog(context, logger):
    if context.readDataFile("zopeorg-various.txt") is None:
        return

    site=context.getSite()
    ct=getToolByName(site, "portal_catalog")
    ct.refreshCatalog()
    logger.info('Site re-catalogued.')

