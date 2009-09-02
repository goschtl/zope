portal = context.portal_url.getPortalObject()

query = dict(portal_type='News Item',
            path='/'.join(portal.news.getPhysicalPath()))
brains = portal.portal_catalog(**query)
return [b.getObject() for b in brains]

