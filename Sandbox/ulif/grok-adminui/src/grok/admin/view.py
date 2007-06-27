import grok
from grok.admin.docgrok import DocGrok, DocGrokPackage, DocGrokModule, getThingsType
from grok.admin.docgrok import DocGrokClass, DocGrokInterface

import zope.component
from zope.app.folder.interfaces import IRootFolder

from zope.app import zapi
from zope.app.applicationcontrol.interfaces import IServerControl
from zope.app.applicationcontrol.applicationcontrol import applicationController
from zope.app.applicationcontrol.runtimeinfo import RuntimeInfo
from zope.app.applicationcontrol.browser.runtimeinfo import RuntimeInfoView

from zope.interface.interface import InterfaceClass
from zope.app.apidoc import utilities, codemodule
from zope.app.apidoc.utilities import getPythonPath, renderText, columnize
from zope.app.apidoc.codemodule.module import Module
from zope.app.apidoc.codemodule.class_ import Class
from zope.app.apidoc.codemodule.function import Function
from zope.app.apidoc.codemodule.text import TextFile
from zope.app.apidoc.codemodule.zcml import ZCMLFile

from zope.proxy import removeAllProxies

grok.context(IRootFolder)
grok.define_permission('grok.ManageApplications')



class Add(grok.View):
    grok.require('grok.ManageApplications')

    def update(self, inspectapp=None, application=None):
        if inspectapp is not None:
            self.redirect( self.url("docgrok") + "/%s/index"%(application.replace('.','/'),))
        return 

    def render(self, application, name, inspectapp=None):
        if name is None or name == "":
            self.redirect(self.url(self.context))
            return
        app = zope.component.getUtility(grok.interfaces.IApplication,
                                        name=application)
        self.context[name] = app()
        self.redirect(self.url(self.context))

class Delete(grok.View):
    grok.require('grok.ManageApplications')

    def render(self, items=None):
        if items is None:
            self.redirect(self.url(self.context))
            return
        if not isinstance(items, list):
            items = [items]
        for name in items:
            del self.context[name]
        self.redirect(self.url(self.context))

class GAIAView(grok.View):
    """A grok.View with a special application_url.

    We have to compute the application_url different from common
    grok.Views, because we have no root application object in the
    adminUI. To avoid mismatch, we also call it 'root_url'.
    """
    def root_url(self, name=None):
        obj = self.context
        result = ""
        while obj is not None:
            if __grok_context__.providedBy(obj):
                return self.url(obj, name)
            obj = obj.__parent__
        raise ValueError("No application nor root element found.")


class Index(GAIAView):
    """A redirector to the real frontpage.
    """
    grok.name('index.html') # the root folder isn't a grok.Model
    grok.require('grok.ManageApplications')

    def update(self):
        apps = zope.component.getAllUtilitiesRegisteredFor(
            grok.interfaces.IApplication)
        self.applications = ("%s.%s" % (x.__module__, x.__name__)
                             for x in apps)
        # Go to the first page immediatly...
        self.redirect(self.url('appsindex'))


class AppsIndex(GAIAView):
    """View for application management."""

    grok.name('appsindex')
    grok.require('grok.ManageApplications')

    def getDocOfApp(self, apppath, headonly = True):
        from grok.admin import docgrok
        doctor = docgrok.handle( apppath )
        result = doctor.getDoc( headonly)
        if result is None:
            result = ""
        return result

    def update(self):
        apps = zope.component.getAllUtilitiesRegisteredFor(
            grok.interfaces.IApplication)
        self.applications = ({'name': "%s.%s" % (x.__module__, x.__name__),
                              'docurl':("%s.%s" % (x.__module__, x.__name__)).replace( '.', '/')}
                             for x in apps)

class Z3Index(GAIAView):
    """Zope3 management screen."""
    grok.name('z3index')
    grok.require('grok.ManageApplications')

    riv = RuntimeInfoView()

    def serverControl(self):
        return zapi.getUtility(IServerControl)

    def runtimeInfo(self):
        self.riv.context = applicationController
        return self.riv.runtimeInfo()

    def update(self, time=None, restart=None, shutdown=None):
        self.ri = self.runtimeInfo()

        if time is None:
            return
        try:
            time = int(time)
        except:
            return
        control = self.serverControl()
        if restart is not None:
            control.restart(time)
        elif shutdown is not None:
            control.shutdown(time)
        self.redirect(self.url())



class Macros(GAIAView):
    """Only to contain the standard macros."""
    grok.context(IRootFolder)
    pass


class DocGrokView(GAIAView):
    """The doctor is in.
    """
    grok.context(DocGrok)
    grok.name( 'index' )

    def getDoc(self, text=None, heading_only=False):
        """Get the doc string of the module STX formatted.
        """
        if text is None:
            return None
            if hasattr( self.context, "apidoc") and hasattr(
                self.context.apidoc, "getDocString" ):
                text = self.context.apidoc.getDocString()
            else:
                return None
        lines = text.strip().split('\n')
        if len(lines) and heading_only:
            # Find first empty line to separate heading from trailing text.
            headlines = []
            for line in lines:
                if line.strip() == "":
                    break
                headlines.append(line)
            lines = headlines
        # Get rid of possible CVS id.
        lines = [line for line in lines if not line.startswith('$Id')]
        return renderText('\n'.join(lines), self.context.getPath())
        

    def getDocHeading( self, text=None):
        return self.getDoc( text, True)

    def getPathParts(self, path=None):
        """Get parts of a dotted name as url and name parts.
        """
        if path is None:
            path = self.context.path
        result = []
        part_path = ""
        for part in path.split( '.' ):
            name = part
            if part_path != "":
                name = "." + part
            part_path += part
            result.append( {
                'name':name,
                'url':"/docgrok/%s" % (part_path,)
                })
            part_path += "/"
        return result

    def getEntries( self, columns=True ):
        """Return info objects for all modules and classes in the
        associated apidoc container.
        """
        if not hasattr(self.context, "apidoc") or not hasattr(self.context.apidoc, "items"):
            return None
        entries = [{'name': name,
                    'obj' : obj,
                    'doc' : (
                         hasattr(obj,"getDocString") and self.getDocHeading(obj.getDocString())) or  (
                         hasattr(obj, "getDoc") and isinstance(
                         removeAllProxies(obj), InterfaceClass) and self.getDocHeading(obj.getDoc())) or  None,
                    # only for interfaces; should be done differently somewhen
                    'path': getPythonPath(removeAllProxies(obj)),
                    'url': ("%s.%s" % (self.context.path, name)).replace('.','/'),
                    'ispackage': getThingsType(
                         "%s.%s" % (self.context.path,name) ) == "package",
                    'ismodule': getThingsType(
                         "%s.%s" % (self.context.path,name) ) == "module",
                    'isinterface': isinstance(
                         removeAllProxies(obj), InterfaceClass),
                    'isclass': isinstance(obj, Class),
                    'isfunction': isinstance(obj, Function),
                    'signature' : isinstance(obj, Function) and obj.getSignature() or None,
                    'istextfile': isinstance(obj, TextFile),
                    'iszcmlfile': isinstance(obj, ZCMLFile)}
                   for name, obj in self.context.apidoc.items()]
        entries.sort(lambda x, y: cmp(x['name'], y['name']))
        #if columns:
        #    entries = columnize(entries)
        return entries


    def update(self):
        self.docgrok_root = self.context._traversal_root
        self.app_root = self.docgrok_root.__parent__
        pass


class DocGrokPackageView(DocGrokView):
    grok.context(DocGrokPackage)
    grok.name( 'index' )

class DocGrokModuleView(DocGrokView):
    grok.context(DocGrokModule)
    grok.name( 'index' )

class DocGrokClassView(DocGrokView):
    grok.context(DocGrokClass)
    grok.name( 'index' )

    def getBases(self):
        return self._listClasses(self.context.apidoc.getBases())

    def getInterfaces(self):
        return self._listClasses([iface for iface in self.context.apidoc.getInterfaces()])

    def _listClasses(self, classes):
        info = []
        for cls in classes:
            unwrapped_cls = removeAllProxies(cls)
            fullpath = getPythonPath(unwrapped_cls)
            if not fullpath:
                continue
            path, name = fullpath.rsplit('.', 1)
            info.append( {
                'path': path or None,
                'path_parts' : self.getPathParts( path ) or None,
                'name': name,
                'url': fullpath and fullpath.replace('.','/') or None,
                'doc': self.getDocHeading( cls.__doc__ ) or None
                })
        return info

class DocGrokInterfaceView(DocGrokClassView):
    grok.context(DocGrokInterface)
    grok.name( 'index' )
