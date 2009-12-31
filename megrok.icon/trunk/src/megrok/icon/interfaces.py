# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface
from zope.container.constraints import contains

ALLOWED = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']


class IIcon(Interface):
    """An icon resource.
    """
    name = schema.TextLine(
        title=u"Identifier of the icon.",
        description=u"",
        required=True)

    path = schema.URI(
        title=u"Path of the resource",
        required=True)

    size = schema.Int(
        title=u"Size in octet",
        required=False)


class IIconRegistryStorage(Interface):
    """The icon registry container.
    """
    contains(IIcon)


class IIconRegistry(Interface):
    """The icon registry.
    """
    def add(name, path):
        """Adds an icon to the registry.
        """

    def get(name):
        """Returns an IIcon component from the registry,
        with the given name.
        """

    allowed = schema.List(
        title=u"Mimetypes allowed for icon files.",
        default=ALLOWED,
        required=True)

    registry = schema.Object(
        schema=IIconRegistryStorage,
        title=u"Icon resource registry",
        required=True)
