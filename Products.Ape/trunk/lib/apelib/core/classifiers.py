##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Standard classifiers.

$Id$
"""

from apelib.core.interfaces import IConfigurableClassifier, IClassifier
from apelib.core.interfaces import ClassificationError, ConfigurationError


class SimpleClassifier:
    """Classifies objects based purely on the class of the object.
    """

    __implements__ = IConfigurableClassifier
    gateway = None

    def __init__(self, gw):
        self._class_to_mapper = {}  # class name -> mapper_name
        self.gateway = gw

    def add_store_rule(self, class_name, mapper_name, *args, **kw):
        self._class_to_mapper[class_name] = mapper_name

    def add_load_rule(self, criterion, value, mapper_name):
        pass

    def set_option(self, mapper_name, option, value):
        raise ConfigurationError("No options available")

    def classify_object(self, event):
        c = event.obj.__class__
        class_name = "%s.%s" % (c.__module__, c.__name__)
        mapper_name = self._class_to_mapper[class_name]
        return {"class_name": class_name, "mapper_name": mapper_name}

    def classify_state(self, event):
        classification, serial = self.gateway.load(event)
        class_name = classification["class_name"]
        mapper_name = self._class_to_mapper[class_name]
        return {"class_name": class_name, "mapper_name": mapper_name}

