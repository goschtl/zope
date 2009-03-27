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
"""Base Classes Feature

$Id$
"""
import lxml.etree
import pkg_resources
import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty
from z3c.feature.core import interfaces, xml

MISSING_DOCUMENTATION = """
Sorry, but the authors of the \"%s\" feature are
big meanies who don't like to make software
accessible."""

class BaseFeature(object):
    zope.interface.implements(
        interfaces.IFeature, interfaces.IBaseFeatureSchema)

    featureSingleton = FieldProperty(interfaces.IFeature['featureSingleton'])
    featureDependencies = ()

    @property
    def featureTitle(self):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        return self.__class__.__name__

    @property
    def featureDocumentation(self):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        return MISSING_DOCUMENTATION  % self.featureTitle

    @classmethod
    def fromXMLNode(cls, node, omit=()):
        feature = cls()
        schema = getFeatureSchema(feature)
        data = xml.extractData(node, schema)
        for fieldName in schema:
            if fieldName in omit:
                continue
            value = data.get(fieldName)
            if value:
                setattr(feature, fieldName, value)
        return feature

    @classmethod
    def fromXML(cls, xml):
        tree = lxml.etree.fromstring(xml)
        return cls.fromXMLNode(tree)

    def findEntryPoint(self):
        set = pkg_resources.working_set
        for entryPoint in set.iter_entry_points(interfaces.FEATURE_GROUP):
            if entryPoint.load() == self.__class__:
                return entryPoint.dist.project_name, entryPoint.name
        return None, None

    def toXML(self, asString=False, prettyPrint=False):
        feature = lxml.etree.Element('feature')
        egg, name = self.findEntryPoint()
        feature.set('type', egg + ':' + name if egg and name else 'unknown')
        schema = getFeatureSchema(self)
        for fieldName in zope.schema.getFields(schema):
            if fieldName in interfaces.IFeature:
                continue

            value = getattr(self, fieldName)
            if value != schema[fieldName].default:
                featureOption = lxml.etree.SubElement(feature, fieldName)
                if isinstance(value, (list, tuple, set)):
                    for item in value:
                        itemElem = lxml.etree.SubElement(featureOption, 'item')
                        itemElem.text = str(item)
                else:
                    featureOption.text = str(value)
        if asString:
            return lxml.etree.tostring(feature, pretty_print=prettyPrint)
        return feature

    def update(self, features=None):
        """See ``z3c.feature.core.interfaces.IFeature``"""

    def _applyTo(self, context):
        pass

    def applyTo(self, context):
        """See ``z3c.feature.core.interfaces.IFeature``"""
        if interfaces.IHaveAppliedFeatures.providedBy(context):
            context.appliedFeatures.append(self)
        self._applyTo(context)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.featureTitle)


def getFeatureSchema(feature):
    if isinstance(feature, type):
        ifaces = zope.interface.implementedBy(feature).flattened()
    else:
        ifaces = zope.interface.providedBy(feature).flattened()
    for iface in ifaces:
        if interfaces.IFeatureSchema.providedBy(iface):
            return iface
    return None


def getFeatureTypes(feature):
    return [iface
            for iface in zope.interface.providedBy(feature).flattened()
            if interfaces.IFeatureType.providedBy(iface)]


def resolveDependencies(features, resolution=None, seen=None, types=None,
                        all=None):
    # List of all features.
    if all is None:
        all = features
    # List of all feature types that have been found on singletons.
    if types is None:
        types = []
    # List of features that have been resolved in the correct order.
    if resolution is None:
        resolution = []
    # A list of seen features for a particular dependency sub-path.
    if seen is None:
        seen = []
    # Loop through all features and resolve them.
    for name, feature in features.items():
        # If the feature is a singleton record its types.
        if feature.featureSingleton:
            for type in getFeatureTypes(feature):
                if type in types:
                    raise interfaces.DuplicateFeatureConflictError(type)
                types.append(type)
        # If a feature is already resolved, skip the feature.
        if feature in resolution:
            continue
        # If we have seen the feature already, we have a cycle.
        if feature in seen:
            raise interfaces.CyclicDependencyError(seen[seen.index(feature):])
        # If we do not have a cycle, add the feature to the list of seen ones
        seen.append(feature)
        # Resolve the dependencies of all children.
        if feature.featureDependencies:
            try:
                deps = dict(
                    [(name, all[name]) for name in feature.featureDependencies])
            except KeyError:
                raise interfaces.MissingFeatureDependencyError(feature, name)
            resolveDependencies(deps, resolution, seen, types, all)
        # Add the feature to the resolution.
        if  feature not in resolution:
            resolution.append(feature)
        # Remove the feature from the current dependency path.
        seen.pop()

    return resolution

def applyFeatures(features, project):
    """Apply a list of features to the project."""
    # Make sure the project collects all applied features
    zope.interface.directlyProvides(project, interfaces.IHaveAppliedFeatures)
    project.appliedFeatures = []
    # Apply features one by one.
    featureDict = dict(
        [(feature.findEntryPoint()[1] or 'unknwon-%i' %idx, feature)
         for idx, feature in enumerate(features)])
    for feature in resolveDependencies(featureDict):
        feature.update(featureDict)
        feature.applyTo(project)


class FileBasedTemplateBase(object):

    _filename = None

    def getFeatures(self):
        if self._filename is None:
            raise ValueError("Missing filename attribute.")
        return xml.getFeatures(open(self._filename))


def FileBasedTemplate(filename, title, description):
    FileBasedTemplate = type(
        '<FileBasedTemplate for %s' % filename,
        (FileBasedTemplateBase,),
        dict(title=title,
             description=description,
             _filename=filename))

    zope.interface.classImplements(
        FileBasedTemplate, interfaces.IProjectTemplateProvider)
    return FileBasedTemplate
