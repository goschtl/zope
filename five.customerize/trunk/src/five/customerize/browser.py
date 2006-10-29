import os.path
from Acquisition import aq_inner

from Products.Five.component.interfaces import IObjectManagerSite
from Products.Five.component import findSite
from Products.Five.browser import BrowserView

import zope.interface
import zope.component
import zope.dottedname.resolve
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.browser import absoluteURL
from zope.app.apidoc.presentation import getViews

from five.customerize.zpt import TTWTemplate

def mangleAbsoluteFilename(filename):
    """
    Mangle an absolute filename when the file happens to be in a
    package.  The mangled name will then be of the form::

      <dotted package name>/<base filename>.

    For example, let's take Five's configure.zcml as an example.  We
    assemble it in an OS-independent way so this test works on all
    platforms:
    
      >>> def filesystemPath(*elements):
      ...     return os.path.sep.join(elements)

    We see that the filename is now mangled:

      >>> mangleAbsoluteFilename(filesystemPath(
      ...     '', 'path', 'to', 'Products', 'Five', 'configure.zcml'))
      'Products.Five/configure.zcml'

    The name of a file that's not in a package is returned unchanged:

      >>> not_in_a_package = filesystemPath('', 'path', 'to', 'configure.zcml')
      >>> mangleAbsoluteFilename(not_in_a_package) == not_in_a_package
      True
    """
    if not os.path.isabs(filename):
        raise ValueError("Can only determine package for absolute filenames")
    dir, basename = os.path.split(filename)
    pieces = dir.split(os.path.sep)
    if pieces[0] == '':
        pieces = pieces[1:]
    while pieces:
        try:
            zope.dottedname.resolve.resolve('.'.join(pieces))
            break
        except ImportError:
            pieces = pieces[1:]
    if not pieces:
        return filename
    return '.'.join(pieces) + '/' + basename

class CustomizationView(BrowserView):

    def templateViewRegistrations(self):
        for reg in getViews(zope.interface.providedBy(self.context),
                            IBrowserRequest):
            factory = reg.factory
            while hasattr(factory, 'factory'):
                factory = factory.factory
            #XXX this should really be dealt with using a marker interface
            # on the view factory
            if hasattr(factory, '__name__') and \
                   factory.__name__.startswith('SimpleViewClass'):
                yield reg

    def templateViewRegInfo(self):
        def regkey(reg):
            return reg.name
        for reg in sorted(self.templateViewRegistrations(), key=regkey):
            yield {
                'viewname': reg.name,
                'for': reg.required[0].__identifier__,
                'type': reg.required[1].__identifier__,
                'zptfile': mangleAbsoluteFilename(reg.factory.index.filename),
                'zcmlfile': mangleAbsoluteFilename(reg.info.file)
                }

    def viewClassFromViewName(self, viewname):
        view = zope.component.getMultiAdapter((self.context, self.request),
                                              name=viewname)
        # The view class is generally auto-generated, we usually want
        # the first base class, though if the view only has one base
        # (generally object or BrowserView) we return the full class
        # and hope that it can be pickled
        klass = view.__class__
        base =klass.__bases__[0]
        if base is BrowserView or base is object:
            return klass
        return base

    def templateFromViewName(self, viewname):
        view = zope.component.getMultiAdapter((self.context, self.request),
                                              name=viewname)
        return view.index

    def templateCodeFromViewName(self, viewname):
        template = self.templateFromViewName(viewname)
        return open(template.filename, 'rb').read() #XXX: bad zope

    def permissionFromViewName(self, viewname):
        view = zope.component.getMultiAdapter((self.context, self.request),
                                              name=viewname)
        permissions = view.__class__.__ac_permissions__
        for permission, methods in permissions:
            if methods[0] in ('', '__call__'):
                return permission

    def doCustomizeTemplate(self, viewname):
        # find the nearest site
        site = findSite(self.context, IObjectManagerSite)
        if site is None:
            raise TypeError("No site found")  #TODO find right exception

        # we're using the original filename of the template, not the
        # view name to avoid potential conflicts and/or confusion in
        # URLs
        template = self.templateFromViewName(viewname)
        zpt_id = os.path.basename(template.filename)

        template_file = self.templateCodeFromViewName(viewname)
        viewclass = self.viewClassFromViewName(viewname)
        permission = self.permissionFromViewName(viewname)
        viewzpt = TTWTemplate(zpt_id, template_file, view=viewclass,
                              permission=permission)
        site._setObject(zpt_id, viewzpt) #XXXthere could be a naming conflict
        components = site.getSiteManager()

        # find out the view registration object so we can get at the
        # provided and required interfaces
        for reg in getViews(zope.interface.providedBy(self.context),
                            IBrowserRequest):
            if reg.name == viewname:
                break

        components.registerAdapter(viewzpt, required=reg.required,
                                   provided=reg.provided, name=viewname) #XXX info?

        viewzpt = getattr(site, zpt_id)
        return viewzpt

    def customizeTemplate(self, viewname):
        viewzpt = self.doCustomizeTemplate(viewname)
        # to get a "direct" URL we use aq_inner for a straight
        # acquisition chain
        url = absoluteURL(aq_inner(viewzpt), self.request) + "/manage_workspace"
        self.request.RESPONSE.redirect(url)
