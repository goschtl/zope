##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Evolve the ZODB from Zope X3.0 to a Zope X3.1 compatible format.

$Id$
"""
__docformat__ = "reStructuredText"
from zope.app import zapi
from zope.app.error.error import ErrorReportingUtility
from zope.app.error.interfaces import IErrorReportingUtility
from zope.app.generations.utility import findObjectsProviding
from zope.app.principalannotation import PrincipalAnnotationUtility
from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.app.registration.interfaces import IComponentRegistration
from zope.app.registration.interfaces import ActiveStatus, UnregisteredStatus
from zope.app.site.interfaces import ISite, IServiceRegistration
from zope.app.utility import UtilityRegistration
from zope.app.zopeappgenerations import getRootFolder

generation = 1

def evolve(context):
    """Evolve the ZODB from a Zope X3.0 to a X3.1 compatible format.

    - The Principal Annotation Service was replaced by the Principal
      Annotation Utility. Thus all service registrations have to be changed to
      utility registrations. 

    - The Error Reporting Service was replaced by the Error Reporting
      Utility. Thus, all service registrations have to be changed to utility
      registrations. 

    - Component-based registrations used to keep track of their components via
      the component's path. Now it stores the component directly. All
      registrations are updated to this new format.
    """
    root = getRootFolder(context)

    # Fix up Principal Annotation Service --> Utility 
    # We do this by simply removing old Principal Annotation Services and their
    # registrations and then add a new Principal Annotation utility.
    for site in findObjectsProviding(root, ISite):
        for reg in findObjectsProviding(site.getSiteManager(),
                                        IServiceRegistration):
        
            if reg.name == 'PrincipalAnnotation':
                ann = reg.component
                # Set the registration to unregistered and then delete it
                reg.status = UnregisteredStatus
                del zapi.getParent(reg)[zapi.name(reg)]
                # Get the instance dictionary from the old principal
                # annotation service and then delete the service
                props = ann.__dict__
                name = zapi.name(ann)
                folder = zapi.getParent(ann)
                del folder[name]


                # Only add a new principal annotation utility, if there is none.
                utils = [obj for obj in folder.values()
                         if isinstance(obj, PrincipalAnnotationUtility)]
                if len(utils) == 0:
                    # Create the principal annotation utility and set its
                    # properties
                    utility = PrincipalAnnotationUtility()
                    utility.__dict__.update(props)
                    folder[name] = utility
                    # Register the utility and set the registration active
                    reg = UtilityRegistration('', IPrincipalAnnotationUtility,
                                              utility)
                    reg_manager = folder.getRegistrationManager() 
                    key = reg_manager.addRegistration(reg)
                    reg_manager[key].status = ActiveStatus


    # Fix up Error Reporting Service --> Utility 
    # We do this by simply removing old Error Reporting Services and their
    # registrations and then add a new error reporting utility.
    for site in findObjectsProviding(root, ISite):
        for reg in findObjectsProviding(site.getSiteManager(),
                                        IServiceRegistration):
        
            if reg.name == 'ErrorLogging':
                errors = reg.component
                # Set the registration to unregistered and then delete it
                reg.status = UnregisteredStatus
                del zapi.getParent(reg)[zapi.name(reg)]
                # Get the properties from the old error reporting service and
                # delete it
                props = errors.getProperties()
                folder = zapi.getParent(errors)
                del folder[zapi.name(errors)]

                # Only add a new error reporting utility, if there is none.
                if 'ErrorReporting' not in folder:
                    # Create the error reporting utility and set its properties
                    utility = ErrorReportingUtility()
                    utility.setProperties(**props)
                    folder['ErrorReporting'] = utility
                    # Register the utility and set the registration active
                    reg = UtilityRegistration('', IErrorReportingUtility,
                                              utility)
                    reg_manager = folder.getRegistrationManager() 
                    key = reg_manager.addRegistration(reg)
                    reg_manager[key].status = ActiveStatus


    # Fix up registration `componentPath` --> `component`
    sites = findObjectsProviding(root, ISite)
    for site in sites:
        registrations = findObjectsProviding(site.getSiteManager(),
                                             IComponentRegistration)
        for reg in registrations:
            if reg._BBB_componentPath is not None:
                reg.component = reg.getComponent()
