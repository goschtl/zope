##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Meta Data Feature

$Id$
"""
import os
import types
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.builder.core import project, buildout
from z3c.builder.core.base import getTemplatePath, FileBuilder
from z3c.builder.core.interfaces import IFileBuilder
from z3c.feature.core import base, interfaces, xml


METADATA_FEATURE_DOCUMENTATION = """
The Metadata feature sets up the setup.py file which is what
setuptools uses to generate distributable python eggs.
"""

COMMENT_HEADER_ZPL_DOCUMENTATION = """
The Zope Public License file header looks something like this::

%(header)s
"""

PROPRIETARY_HEADER_DOCUMENTATION = """
The proprietary header looks something like this::

%(header)s
"""

DOCUMENTATION_FEATURE_DOCUMENTATION = """
The ReSTructured Text Documentation feature hooks up scripts
for generating html (or latex for that matter) documentation
from ReSTructured text files using Sphinx.  There are a few
pieces involved in this hookup:

  #. ``buildout.cfg`` **part section**

       This looks something like::

         [docs]
         recipe = z3c.recipe.sphinxdoc
         eggs = yourproject [docs]
                z3c.recipe.sphinxdoc
         default.css =
         layout.html =

       This buildout part section will generate a script in the
       bin directory called ``docs`` which you can run liket his::

         $ ./bin/docs

       Documentation will be put into the ``parts/docs/`` directory, with
       one directory for each package specified in the eggs parameter of
       the docs section.  See the documentation for z3c.recipe.sphinxdoc
       for more information.  It can be found at

         http://pypi.python.org/pypi/z3c.recipe.sphinxdoc

  #. ``setup.py extras_require`` **section**

       For the docs to build correctly, there must be a ``docs`` section in
       ``extras_require`` that pulls in the Sphinx dependencies.

  #. ``index.txt`` **file in project src**

       An ``index.txt`` file will be added to the src directory.  This
       serves as the root document used by Sphinx to generate all the
       documentation.  See the Sphinx documentation for what sort of things
       you can put in here at

         http://sphinx.pocoo.org/
"""

class MetaDataFeature(base.BaseFeature):
    zope.interface.implements(interfaces.IMetaDataFeature)

    version = FieldProperty(interfaces.IMetaDataFeature['version'])
    license = FieldProperty(interfaces.IMetaDataFeature['license'])
    url = FieldProperty(interfaces.IMetaDataFeature['url'])
    classifiers = FieldProperty(interfaces.IMetaDataFeature['classifiers'])
    keywords = FieldProperty(interfaces.IMetaDataFeature['keywords'])
    author = FieldProperty(interfaces.IMetaDataFeature['author'])
    author_email = FieldProperty(interfaces.IMetaDataFeature['author_email'])
    description = FieldProperty(interfaces.IMetaDataFeature['description'])
    commentHeader = FieldProperty(interfaces.IMetaDataFeature['commentHeader'])
    namespace_packages = FieldProperty(
        interfaces.IMetaDataFeature['namespace_packages'])
    install_requires = FieldProperty(
        interfaces.IMetaDataFeature['install_requires'])
    extras_require = FieldProperty(interfaces.IMetaDataFeature['extras_require'])

    featureTitle = u'Metadata'
    featureDocumentation = METADATA_FEATURE_DOCUMENTATION

    @classmethod
    def fromXMLNode(cls, node, omit=()):
        feature = super(MetaDataFeature, cls).fromXMLNode(
            node,
            omit=('classifiers', 'extras_require'))

        schema = base.getFeatureSchema(feature)
        data = xml.extractData(node, schema)
        classifiers = data.get('classifiers')

        feature.classifiers = set()
        if classifiers:
            feature.classifiers = [c.strip() for c in classifiers.split('\n')]
        return feature

    def _applyTo(self, context):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        # Assign all meta data to setup.
        for name in ('version', 'license', 'url', 'keywords', 'author',
                     'author_email', 'description', 'namespace_packages',
                     'install_requires','extras_require'):
            value = getattr(self, name)
            if value is not None:
                setattr(context.setup, name, value)
        # Set the comment header.
        if self.commentHeader is not None:
            context.commentHeader = self.commentHeader


class CommentHeaderZPLFeature(base.BaseFeature):
    zope.interface.implements(interfaces.ICommentHeaderZPLFeature)

    _template = unicode(open(getTemplatePath('zpl-header.py')).read())

    year = FieldProperty(interfaces.ICommentHeaderZPLFeature['year'])
    author = FieldProperty(interfaces.ICommentHeaderZPLFeature['author'])

    featureTitle = u'ZPL Header'

    @property
    def featureDocumentation(self):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        header = '  ' + self.renderCommentHeader().replace('\n', '\n  ')
        return COMMENT_HEADER_ZPL_DOCUMENTATION % {'header':header}

    def renderCommentHeader(self):
        return self._template % dict(year=self.year,
                                     author=self.author)

    def _applyTo(self, context):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        context.commentHeader = self.renderCommentHeader()


class ProprietaryHeaderFeature(base.BaseFeature):
    zope.interface.implements(interfaces.IProprietaryHeaderFeature)

    _template = unicode(open(getTemplatePath('proprietary-header.py')).read())

    year = FieldProperty(interfaces.IProprietaryHeaderFeature['year'])
    company = FieldProperty(interfaces.IProprietaryHeaderFeature['company'])
    location = FieldProperty(interfaces.IProprietaryHeaderFeature['location'])

    featureTitle = u'Proprietary Header'

    @property
    def featureDocumentation(self):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        header = '  ' + self.renderCommentHeader().replace('\n', '\n  ')
        return PROPRIETARY_HEADER_DOCUMENTATION % {'header':header}

    def renderCommentHeader(self):
        return self._template % dict(year=self.year,
                                     company=self.company,
                                     location=self.location)

    def _applyTo(self, context):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        context.commentHeader = self.renderCommentHeader()


class DocumentationFileBuilder(FileBuilder):

    template = os.path.join(
        os.path.dirname(__file__), 'file-templates', 'index-template.txt')

    def update(self):
        project = self.getProject()
        self.title = project.name + ' Documentation'
        self.TOC = []
        for builder in self.__parent__.values():
            if (IFileBuilder.providedBy(builder) and
                builder.filename.endswith('.txt') and
                builder is not self):

                self.TOC.append(builder.filename[:-4])

    def render(self):
        heading = '%(border)s\n%(title)s\n%(border)s' % dict(
            border='='*len(self.title),
            title=self.title)
        TOC = '\n   '.join(self.TOC)
        return open(self.template).read() % dict(heading=heading,
                                                 TOC=TOC)

class DocumentationFeature(base.BaseFeature):
    zope.interface.implements(interfaces.IDocumentationFeature)

    layoutTemplatePath = FieldProperty(
        interfaces.IDocumentationFeature['layoutTemplatePath'])
    cssPath = FieldProperty(
        interfaces.IDocumentationFeature['cssPath'])
    additionalEggs = FieldProperty(
        interfaces.IDocumentationFeature['additionalEggs'])

    featureTitle = u'Restructured Text Documentation'
    featureDocumentation = DOCUMENTATION_FEATURE_DOCUMENTATION

    def _applyTo(self, context):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        docsPart = buildout.PartBuilder(u'docs')
        docsPart.addValue('recipe', 'z3c.recipe.sphinxdoc')
        eggs = [context.name+' [docs]'] + (self.additionalEggs or [])
        eggsString = 'z3c.recipe.sphinxdoc'
        for egg in eggs:
            eggsString += '\n       '+egg
        docsPart.addValue('eggs', eggsString)
        docsPart.addValue('layout.html', self.layoutTemplatePath or '')
        docsPart.addValue('default.css', self.cssPath or '')
        context.buildout.add(docsPart)

        context.setup.addExtrasRequires('docs', ['Sphinx'])

        indexBuilder = DocumentationFileBuilder(u'index.txt')
        context.package.add(indexBuilder)
