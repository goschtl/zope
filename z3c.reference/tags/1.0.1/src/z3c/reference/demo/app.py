##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: __init__.py 72084 2007-01-18 01:02:26Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

from zope import interface

from zope.schema.fieldproperty import FieldProperty
from zope.location.interfaces import ILocation

from zope.app.folder.folder import Folder
from zope.app.file.image import Image

from z3c.reference.demo.interfaces import (IDemoFolder,
                                           IDemoImage)
from z3c.reference.interfaces import IReferenced

from lovely.relation.dataproperty import DataRelationPropertyOut
from lovely.relation.property import (FieldRelationManager,
                                      RelationPropertyIn)


previewRelation = FieldRelationManager(IDemoFolder['previewImage'],
                                       IReferenced['viewReferences'],
                                      )

assetsRelation = FieldRelationManager(IDemoFolder['assets'],
                                      IReferenced['viewReferences'],
                                     )


class DemoFolder(Folder):
    """Demo folder implementation."""
    interface.implements(IDemoFolder, IReferenced)

    previewImage = DataRelationPropertyOut(previewRelation,
                                           relType='folder.previewImage',
                                          )
    assets       = DataRelationPropertyOut(assetsRelation,
                                           relType='folder.assets',
                                          )

    viewReferences = RelationPropertyIn(assetsRelation)


class DemoImage(Image):
    """Demo image implementation."""
    interface.implements(IDemoImage, IReferenced, ILocation)

    __name__ = __parent__ = None

    viewReferences = RelationPropertyIn(previewRelation)

