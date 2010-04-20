##############################################################################
#
# Copyright (c) 2006, 2007 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Task Service Implementation

"""
__docformat__ = 'restructuredtext'

from z3c.taskqueue import interfaces
from zope import component
from zope.app.publication.zopepublication import ZopePublication
import logging
import zope.interface
import zope.location


log = logging.getLogger('z3c.remotetask')


def databaseOpened(event):
    """Start the queue processing services based on the
       settings in zope.conf"""
    log.info('handling event IDatabaseOpenedEvent')

    root_folder = getRootFolder(event)

    from zope.app.appsetup.product import getProductConfiguration
    configuration = getProductConfiguration('z3c.taskqueue')
    startSpecifications = getStartSpecifications(configuration)

    for siteName, serviceName in startSpecifications:
        serviceCount = 0
        sites = getSites(siteName, root_folder)
        for site in sites:
            if serviceName == '*':
                services = getAllServices(site, root_folder)
            else:
                service = getService(site, serviceName)
                if service == None:
                    services = []
                else:
                    services = [service]
            serviceCount += startServices(services)

        if (siteName == "*" or serviceName == "*") and serviceCount == 0:
            msg = 'no services started by directive %s@%s'
            log.warn(msg % (siteName, serviceName))


def getRootFolder(event):
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    return root_folder


def getStartSpecifications(configuration):
    """get a list of sites/services to start"""

    autostartParts = []
    if configuration is not None:
        autostart = configuration.get('autostart', '')
        autostartParts = [name.strip()
                        for name in autostart.split(',')]

    result = [name.split('@') for name in autostartParts if name]
    return result


def getSites(siteName, root_folder):
    # we search only for sites at the database root level
    if siteName == '':
        sites = [root_folder]
    elif siteName == '*':
        sites = getAllSites(root_folder)
    else:
        site = getSite(siteName, root_folder)
        if site == None:
            sites = []
        else:
            sites = [site]
    return sites


def getAllSites(root_folder):
    sites = []
    sites.append(root_folder)
    root_values = root_folder.values()
    for folder in root_values:
        if zope.location.interfaces.ISite.providedBy(folder):
            sites.append(folder)
    return sites


def getSite(siteName, root_folder):
    try:
        site = root_folder.get(siteName)
    except KeyError:
        log.error('site %s not found' % siteName)
        site = None
    return site


def getAllServices(site, root_folder):
    sm = site.getSiteManager()
    services = list(
        sm.getUtilitiesFor(interfaces.ITaskService))
    root_sm = root_folder.getSiteManager()
    if sm != root_sm:
        # filter out services defined in root
        rootServices = list(root_sm.getUtilitiesFor(
            interfaces.ITaskService))
        services = [s for s in services
                       if s not in rootServices]
    return services


def getService(site, serviceName):
    service = component.queryUtility(interfaces.ITaskService,
        context=site, name=serviceName)
    if service is not None:
        service = (serviceName, service)
    else:
        csName = getattr(site, '__name__', '')
        if csName is None:
            csName = 'root'
        msg = 'service %s on site %s not found'
        log.error(msg % (serviceName, csName))
        service = None
    return service


def startServices(services):
    serviceCount = 0
    for srvname, service in services:
        if not service.isProcessing():
            service.startProcessing()
            serviceCount += 1
    return serviceCount
