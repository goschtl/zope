##############################################################################
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""WebDAV method PROPFIND

The propfind XML element conforms to the following DTD snippet

  <!ELEMENT propfind ( propname | (allprop, include?) | prop ) >
  <!ELEMENT propname EMPTY >
  <!ELEMENT allprop EMPTY >
  <!ELEMENT include ANY >
  <!ELEMENT prop ANY >

All the render*(ob, req, extra) know how to render the requested properties
requested by the PROPFIND method.

  renderPropnames(ob, req, ignore) - extra argument is ignored.

  renderAllProperties(ob, req, include) - extra argument is a list of all
                                          the properties that must be rendered.

  renderSelectedProperties(ob, req, props) - extra argument is a list of all
                                             the properties to render.

And all these methods return a zope.webdav.utils.IResponse implementation.

$Id$
"""
__docformat__ = 'restructuredtext'

import sys

from zope import interface
from zope import component
from zope.app.container.interfaces import IReadContainer

from zope.etree.interfaces import IEtree
import zope.webdav.utils
import zope.webdav.interfaces
import zope.webdav.properties

DEFAULT_NS = "DAV:"

class PROPFIND(object):
    """
    PROPFIND handler for all objects.

    The PROPFIND method handles parsing of the XML body and then calls the
    
    """
    interface.implements(zope.webdav.interfaces.IWebDAVMethod)
    component.adapts(interface.Interface, zope.webdav.interfaces.IWebDAVRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getDepth(self):
        # default is infinity.
        return self.request.getHeader("depth", "infinity")

    def PROPFIND(self):
        if len(self.request.bodyStream.getCacheStream().read()) > 0 and \
               self.request.content_type not in ("text/xml", "application/xml"):
            raise zope.webdav.interfaces.BadRequest(
                self.request,
                message = u"PROPFIND requires a valid XML request")

        depth = self.getDepth()
        if depth not in ("0", "1", "infinity"):
            raise zope.webdav.interfaces.BadRequest(
                self.request, message = u"Invalid Depth header supplied")

        propertiesFactory = None
        extraArg = None

        propfind = self.request.xmlDataSource
        if propfind is not None:
            if propfind.tag != "{DAV:}propfind":
                raise zope.webdav.interfaces.UnprocessableError(
                    self.context,
                    message = u"Request is not a `propfind' XML element.")
            properties = propfind[0]
            if properties.tag == "{DAV:}propname":
                propertiesFactory = self.renderPropnames
            elif properties.tag == "{DAV:}allprop":
                propertiesFactory = self.renderAllProperties
                includes = propfind.findall("{DAV:}include")
                if includes: # we have "DAV:include" properties
                    extraArg = includes[0]
            elif properties.tag == "{DAV:}prop":
                if len(properties) == 0:
                    ## XXX - does this code correspond to the protocol.
                    propertiesFactory = self.renderAllProperties
                else:
                    propertiesFactory = self.renderSelectedProperties
                    extraArg = properties
            else:
                raise zope.webdav.interfaces.UnprocessableError(
                    self.context,
                    message = u"Unknown propfind property element.")
        else:
            propertiesFactory = self.renderAllProperties

        multistatus = zope.webdav.utils.MultiStatus()
        responses = self.handlePropfindResource(
            self.context, self.request, depth, propertiesFactory, extraArg)
        multistatus.responses.extend(responses)

        etree = component.getUtility(IEtree)

        self.request.response.setStatus(207)
        self.request.response.setHeader("content-type", "application/xml")
        ## Is UTF-8 encoding ok here or is there a better way of doing this.
        return etree.tostring(multistatus(), encoding = "utf-8")

    def handlePropfindResource(self, ob, req, depth, \
                               propertiesFactory, extraArg):
        """
        Recursive method that collects all the `response' XML elements for
        the current PROPFIND request.

        `propertiesFactory' is the method that is used to generated the
        `response' XML element for one resource. It takes the resource,
        request and `extraArg' used to pass in specific information about
        the properties we want to return.
        """
        responses = [propertiesFactory(ob, req, extraArg)]

        if depth in ("1", "infinity") and IReadContainer.providedBy(ob):
            subdepth = (depth == "1") and "0" or "infinity"

            for subob in ob.values():
                responses.extend(self.handlePropfindResource(
                    subob, req, subdepth, propertiesFactory, extraArg))

        return responses

    def renderPropnames(self, ob, req, ignore):
        response = zope.webdav.utils.Response(
            zope.webdav.utils.getObjectURL(ob, req))

        for davprop, adapter in \
                zope.webdav.properties.getAllProperties(ob, req):
            davwidget = zope.webdav.properties.getWidget(davprop, adapter, req)
            response.addProperty(200, davwidget.renderName())

        return response

    def renderAllProperties(self, ob, req, include):
        response = zope.webdav.utils.Response(
            zope.webdav.utils.getObjectURL(ob, req))

        for davprop, adapter in \
                zope.webdav.properties.getAllProperties(ob, req):
            if davprop.restricted:
                if include is None or \
                       include.find("{%s}%s" %(davprop.namespace,
                                               davprop.__name__)) is None:
                    continue

            davwidget = zope.webdav.properties.getWidget(davprop, adapter, req)
            response.addProperty(200, davwidget.render())

        return response

    def renderSelectedProperties(self, ob, req, props):
        response = zope.webdav.utils.Response(
            zope.webdav.utils.getObjectURL(ob, req))

        etree = component.getUtility(IEtree)

        for prop in props:
            try:
                davprop, adapter = zope.webdav.properties.getProperty(
                    ob, req, prop.tag, exists = True)
                davwidget = zope.webdav.properties.getWidget(
                    davprop, adapter, req)
                propstat = response.getPropstat(200)
                propstat.properties.append(davwidget.render())
            except Exception, error:
                exc_info = sys.exc_info()

                error_view = component.queryMultiAdapter(
                    (error, req), zope.webdav.interfaces.IDAVErrorWidget)
                if error_view is None:
                    ## XXX - needs testing
                    raise exc_info[0], exc_info[1], exc_info[2]

                propstat = response.getPropstat(error_view.status)
                ## XXX - needs testing
                propstat.responsedescription += error_view.propstatdescription
                response.responsedescription += error_view.responsedescription

                propstat.properties.append(etree.Element(prop.tag))

        return response
