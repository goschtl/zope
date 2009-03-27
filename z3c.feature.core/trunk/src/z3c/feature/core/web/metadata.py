import zope.schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from z3c.form.form import EditForm
from z3c.form.field import Fields
from z3c.form.browser.textlines import TextLinesFieldWidget

from z3c.feature.core.metadata import MetaDataFeature
from z3c.feature.core.metadata import CommentHeaderZPLFeature
from z3c.feature.core.metadata import ProprietaryHeaderFeature
from z3c.feature.core.metadata import DocumentationFeature
from z3c.feature.core.python import PythonInterpreterFeature
from z3c.feature.core import interfaces

licenseVocabulary = SimpleVocabulary([
    SimpleTerm('Aladdin Free Public License (AFPL)'),
    SimpleTerm('DFSG approved'),
    SimpleTerm('Eiffel Forum License (EFL)'),
    SimpleTerm('Free For Educational Use'),
    SimpleTerm('Free For Home Use'),
    SimpleTerm('Free for non-commercial use'),
    SimpleTerm('Freely Distributable'),
    SimpleTerm('Free To Use But Restricted'),
    SimpleTerm('Freeware'),
    SimpleTerm('Netscape Public License (NPL)'),
    SimpleTerm('Nokia Open Source License (NOKOS)'),
    SimpleTerm('Academic Free License (AFL)'),
    SimpleTerm('Apache Software License'),
    SimpleTerm('Apple Public Source License'),
    SimpleTerm('Artistic License'),
    SimpleTerm('Attribution Assurance License'),
    SimpleTerm('BSD License'),
    SimpleTerm('Common Public License'),
    SimpleTerm('Eiffel Forum License'),
    SimpleTerm('GNU Affero General Public License v3'),
    SimpleTerm('GNU Free Documentation License (FDL)'),
    SimpleTerm('GNU General Public License (GPL)'),
    SimpleTerm('GNU Library or Lesser General Public License (LGPL)'),
    SimpleTerm('IBM Public License'),
    SimpleTerm('Intel Open Source License'),
    SimpleTerm('Jabber Open Source License'),
    SimpleTerm('MIT License'),
    SimpleTerm('MITRE Collaborative Virtual Workspace License (CVW)'),
    SimpleTerm('Motosoto License'),
    SimpleTerm('Mozilla Public License 1.0 (MPL)'),
    SimpleTerm('Mozilla Public License 1.1 (MPL 1.1)'),
    SimpleTerm('Nethack General Public License'),
    SimpleTerm('Nokia Open Source License'),
    SimpleTerm('Open Group Test Suite License'),
    SimpleTerm('Python License (CNRI Python License)'),
    SimpleTerm('Python Software Foundation License'),
    SimpleTerm('Qt Public License (QPL)'),
    SimpleTerm('Ricoh Source Code Public License'),
    SimpleTerm('Sleepycat License'),
    SimpleTerm('Sun Industry Standards Source License (SISSL)'),
    SimpleTerm('Sun Public License'),
    SimpleTerm('University of Illinois/NCSA Open Source License'),
    SimpleTerm('Vovida Software License 1.0'),
    SimpleTerm('W3C License'),
    SimpleTerm('X.Net License'),
    SimpleTerm('zlib/libpng License'),
    SimpleTerm('Zope Public License'),
    SimpleTerm('Other/Proprietary License'),
    SimpleTerm('Public Domain'),
    ])


class MetaDataWebView(EditForm):

    label = u'Project Metadata'
    template = ViewPageTemplateFile('templates/metadata.pt')
    javascript = ViewPageTemplateFile('templates/metadata.js')
    fields = Fields(zope.schema.Choice(
         __name__='commonLicense',
        title=u'License',
        default=u'GNU General Public License (GPL)',
        vocabulary=licenseVocabulary,
        required=False))

    fields += Fields(interfaces.IMetaDataFeature).select(
        'license','version','description','author',
        'author_email','url','classifiers','keywords',
        'namespace_packages','install_requires',
        'commentHeader')

    fields = fields.select(
        'license','commonLicense','version','description','author',
        'author_email','url','classifiers','keywords',
        'namespace_packages','install_requires',
        'commentHeader')

    fields['keywords'].widgetFactory = TextLinesFieldWidget
    fields['namespace_packages'].widgetFactory = TextLinesFieldWidget
    fields['install_requires'].widgetFactory = TextLinesFieldWidget

    def applyChanges(self, data):
        commonLicense = data.pop('commonLicense')
        data['license'] = data.get('license', commonLicense)
        return super(MetaDataWebView, self).applyChanges(data)


class MetaDataWebFeature(object):
    viewFactory = MetaDataWebView
    contentFactory = MetaDataFeature
    title = u"Metadata"
    description = (u"Let's you modify project metadata used by setuptools "
                   u"such as version number, license information, author "
                   u"information, project description, and more.")


class CommentHeaderZPLWebView(EditForm):
    label = u'Comment Header for the Zope Public License'
    fields = Fields(interfaces.ICommentHeaderZPLFeature).select('year')


class CommentHeaderZPLWebFeature(object):
    viewFactory = CommentHeaderZPLWebView
    contentFactory = CommentHeaderZPLFeature
    title = u"ZPL Header"
    description = u"Adds a ZPL Header to all generated files."



class ProprietaryHeaderWebView(EditForm):
    template = ViewPageTemplateFile("templates/proprietary-header.pt")
    fields = Fields(interfaces.IProprietaryHeaderFeature).select(
        'year','company','location')

    def update(self):
        super(ProprietaryHeaderWebView, self).update()
        self.commentHeader = self.context.renderCommentHeader()

class ProprietaryHeaderWebFeature(object):
    viewFactory = ProprietaryHeaderWebView
    contentFactory = ProprietaryHeaderFeature
    title = u"Proprietary Header"
    description = u"Adds a Proprietary Software Header to all generated files."


class DocumentationWebView(EditForm):
    label = u'Documentation'
    fields = Fields(interfaces.IDocumentationFeature)


class DocumentationWebFeature(object):
    viewFactory = DocumentationWebView
    contentFactory = DocumentationFeature
    title = u"Documentation"
    description = (u"Adds a script for generating project documentation from "
                   u"ReSTructured Text files using Sphinx (just like the python "
                   u"documetation).  Great in combination with the "
                   u"Automated Tests Feature")


