import os
import shutil
import random
import string
import tempfile
import pkg_resources
import docutils.core
from persistent.dict import PersistentDict

from zope.interface import Interface
from zope.schema import ASCIILine
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.interface import implements
from zope.container.btree import BTreeContainer
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.component.hooks import getSite
from zope.location.location import LocationProxy
from zope.component import queryMultiAdapter
from zope.component import provideAdapter
from zope.traversing.api import getParents
from zope.security.proxy import removeSecurityProxy
from zope.app.folder.interfaces import IRootFolder
from zope.schema.fieldproperty import FieldProperty
from zope.container.interfaces import INameChooser

from z3c.pagelet.browser import BrowserPagelet
from z3c.formui.layout import FormLayoutSupport
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.formui.form import Form
from z3c.formui.form import EditForm

from z3c.builder.core.interfaces import IProjectBuilder
from z3c.builder.core.project import BuildoutProjectBuilder
from z3c.boilerweb.interfaces import IBuildSession
from z3c.boilerweb.interfaces import IBuilderBrowserLayer
from z3c.boilerweb.session import SessionProperty
from z3c.feature.core import base, xml, template
from z3c.feature.core.xml import etree
from z3c.feature.core.interfaces import IFeature

WEB_FEATURE_CACHE = {}


def createProject(session):
    builder = BuildoutProjectBuilder(unicode(session.name))
    builder.add(xml.FeatureDocBuilder(u'ZBOILER.txt'))
    base.applyFeatures(session.values(), builder)
    return builder


class BuildSession(BTreeContainer):
    implements(IBuildSession)

    name = FieldProperty(IBuildSession['name'])

    def addFeature(self, entryPoint):
        egg, entry = entryPoint.split(':')
        webFeature = pkg_resources.get_distribution(egg).load_entry_point(
            'z3c.builderweb', entry)()
        newFeature = webFeature.contentFactory()
        WEB_FEATURE_CACHE[newFeature.__class__] = webFeature
        name = INameChooser(self).chooseName(entry, newFeature)
        self[name] = newFeature

    def toXML(self, asString=False, prettyPrint=False):
        root = etree.Element('project')
        root.set('name',self.name)
        for feature in self.values():
            root.append(feature.toXML())
        if asString:
            return etree.tostring(root, pretty_print=prettyPrint)
        return root


def getWebFeatureFor(feature):
    if WEB_FEATURE_CACHE.has_key(feature.__class__):
        return WEB_FEATURE_CACHE[feature.__class__]
    for entryPoint in pkg_resources.working_set.iter_entry_points('z3c.builderweb'):
        # XXX: this is *really* brittle
        webFeature = entryPoint.load()()
        if webFeature.contentFactory == feature.__class__:
            WEB_FEATURE_CACHE[feature.__class__] = webFeature
            return webFeature

class Breadcrumbs(object):

    def crumbs(self):
        result = []
        parents = getParents(self.context)
        for parent in parents + [self.context]:
            if IFeature.providedBy(parent):
                title = getWebFeatureFor(parent).title
            else:
                title = getattr(parent,'name',parent.__name__)
            if not title:
                continue
            result.append(dict(
                url=absoluteURL(parent, self.request),
                title=title))
        return result

class NavMenu(object):

    def items(self):
        site = getSite()
        siteURL = absoluteURL(site, self.request)
        entries = [
            dict(
                url=siteURL+"/index.html",
                title="Home"
                ),
            dict(
                url=siteURL+"/build.html",
                title="Build",
                cssClass='selected' if not IRootFolder.providedBy(self.context) else ''
                ),
            dict(
                url=siteURL+"/about.html",
                title="About"
                ),
            ]
        for entry in entries:
            if entry['url'] == self.request.getURL():
                entry['cssClass'] = 'selected'
        return entries


class FrontPageView(BrowserPagelet):

    def update(self):
        self.projectTemplates = []
        for name, temp in template.getTemplateList().items():
            self.projectTemplates.append(
                dict(name=name,
                     title=temp.title,
                     description=temp.description))


class AboutView(BrowserPagelet):
    pass

class AddFeatureForm(BrowserPagelet):

    def updateFeatures(self):
        self.features = []
        existing = [feature.__class__
                    for feature in self.context.values()
                    if feature.featureSingleton]
        for entryPoint in pkg_resources.working_set.iter_entry_points('z3c.builderweb'):
            name = entryPoint.dist.project_name+':'+entryPoint.name
            factory=entryPoint.load()()
            added = factory.contentFactory in existing
            self.features.append(dict(
                name=name,
                cssClass = 'added' if added else '',
                added = added,
                data=factory))

    def updateActions(self):
        for feature in self.features:
            if feature['name']+'.add' in self.request.form:
                self.context.addFeature(feature['name'])

    def update(self):
        self.updateFeatures()
        self.updateActions()

        self.updateFeatures()


class FeatureView(BrowserPagelet):

    def featureView(self):
        # untrusted code doesn't get to work with security proxied objects.
        context = removeSecurityProxy(self.context)
        egg, entryPoint = context.findEntryPoint()
        webFeatureFactory = pkg_resources.get_distribution(egg).load_entry_point('z3c.builderweb', entryPoint)
        return webFeatureFactory().viewFactory(context, self.request)()

class BuildView(EditForm):

    fields = Fields(IBuildSession).select('name')

    build = SessionProperty('build', key="build")

    def __init__(self, context, request):
        # Since these are third party content items discovered through
        # entry points, there are no security declarations for them.
        # Each component must implement whatever security it needs on
        # its own.
        super(BuildView, self).__init__(removeSecurityProxy(context), request)

    def addFeaturesFromTemplate(self, name):
      provider = template.getTemplate(name)
      for feature in provider.getFeatures().values():
          egg, entry = feature.findEntryPoint()
          name = INameChooser(self.build).chooseName(entry, feature)
          self.build[name] = feature

    def __call__(self):
        template = self.request.get('template')
        if not IBuildSession.providedBy(self.context) or template:

            if self.build and self.request.get('startover'):
                del self.context[self.build.__name__]
                self.build = None

            if not self.build:
                name = ''.join([random.choice(string.letters) for i in xrange(6)])
                self.build = self.context[name] = BuildSession()
                self.build.name = 'helloworld'
                if template:
                    self.addFeaturesFromTemplate(template)
            self.request.response.redirect(absoluteURL(self.build, self.request))
            return
        return super(BuildView, self).__call__()

    def update(self):
        super(BuildView, self).update()
        self.actions['apply'].title = u"Save"

        for featureName in self.context.keys():
            if '%s.delete' % featureName in self.request.form:
                del self.context[featureName]

        self.addFeatureForm = AddFeatureForm(self.context, self.request)
        self.addFeatureForm.update()


class DownloadView(BrowserPagelet):

    def __init__(self, context, request):
        # This is working with third party components that do not
        # have any security definitions.
        self.context = removeSecurityProxy(context)
        self.request = request

    def documentation(self):
        builder = createProject(self.context)
        parts = docutils.core.publish_parts(
            source=builder['ZBOILER.txt'].render(),
            writer_name='html')
        return parts['html_body']

class TarballView(object):

    def __init__(self, context, request):
        # This is working with third party components that do not
        # have any security definitions.
        self.context = removeSecurityProxy(context)
        self.request = request

    def __call__(self):
        builder = createProject(self.context)
        builder.update()
        outputDirectory = tempfile.mkdtemp()
        builder.write(outputDirectory)
        tarballPath = os.path.join(outputDirectory, builder.name)+'.tar.gz'
        os.system('tar -cz --directory=%s -f %s %s' % (outputDirectory, tarballPath, builder.name))
        bytes = open(tarballPath).read()
        shutil.rmtree(outputDirectory)
        self.request.response.setHeader('Content-Type', 'application/x-gzip')
        return bytes


class XMLExportView(object):

    def __init__(self, context, request):
        # This is working with third party components that do not
        # have any security definitions.
        self.context = removeSecurityProxy(context)
        self.request = request

    def __call__(self):
        self.request.response.addHeader('Content-Description', self.context.name+'.xml')
        self.request.response.addHeader('Content-Disposition',
                                        'attachment; filename="%s.xml"' % self.context.name)
        return self.context.toXML(True, True)
