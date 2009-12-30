##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Browser widgets

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.formlibwidget.browser.widget import BrowserWidget, DisplayWidget
from zope.formlibwidget.browser.widget import UnicodeDisplayWidget

from zope.formlibwidget.browser.textwidgets import TextWidget, BytesWidget
from zope.formlibwidget.browser.textwidgets import TextAreaWidget, BytesAreaWidget
from zope.formlibwidget.browser.textwidgets import PasswordWidget, FileWidget
from zope.formlibwidget.browser.textwidgets import ASCIIWidget, ASCIIAreaWidget
from zope.formlibwidget.browser.textwidgets import IntWidget, FloatWidget
from zope.formlibwidget.browser.textwidgets import DecimalWidget
from zope.formlibwidget.browser.textwidgets import DatetimeWidget, DateWidget
from zope.formlibwidget.browser.textwidgets import DatetimeI18nWidget
from zope.formlibwidget.browser.textwidgets import DateI18nWidget
from zope.formlibwidget.browser.textwidgets import DatetimeDisplayWidget
from zope.formlibwidget.browser.textwidgets import DateDisplayWidget
from zope.formlibwidget.browser.textwidgets import BytesDisplayWidget
from zope.formlibwidget.browser.textwidgets import ASCIIDisplayWidget
from zope.formlibwidget.browser.textwidgets import URIDisplayWidget

# Widgets for boolean fields
from zope.formlibwidget.browser.boolwidgets import CheckBoxWidget
from zope.formlibwidget.browser.boolwidgets import BooleanRadioWidget
from zope.formlibwidget.browser.boolwidgets import BooleanSelectWidget
from zope.formlibwidget.browser.boolwidgets import BooleanDropdownWidget

# Choice and Sequence Display Widgets
from zope.formlibwidget.browser.itemswidgets import ItemDisplayWidget
from zope.formlibwidget.browser.itemswidgets import ItemsMultiDisplayWidget
from zope.formlibwidget.browser.itemswidgets import SetDisplayWidget
from zope.formlibwidget.browser.itemswidgets import ListDisplayWidget

# Widgets for fields with vocabularies.
# Note that these are only dispatchers for the widgets below.
from zope.formlibwidget.browser.itemswidgets import ChoiceDisplayWidget
from zope.formlibwidget.browser.itemswidgets import ChoiceInputWidget
from zope.formlibwidget.browser.itemswidgets import CollectionDisplayWidget
from zope.formlibwidget.browser.itemswidgets import CollectionInputWidget
from zope.formlibwidget.browser.itemswidgets import ChoiceCollectionDisplayWidget
from zope.formlibwidget.browser.itemswidgets import ChoiceCollectionInputWidget

# Widgets that let you choose a single item from a list
# These widgets are multi-views on (field, vocabulary)
from zope.formlibwidget.browser.itemswidgets import SelectWidget
from zope.formlibwidget.browser.itemswidgets import DropdownWidget
from zope.formlibwidget.browser.itemswidgets import RadioWidget

# Widgets that let you choose several items from a list
# These widgets are multi-views on (field, vocabulary)
from zope.formlibwidget.browser.itemswidgets import MultiSelectWidget
from zope.formlibwidget.browser.itemswidgets import MultiSelectSetWidget
from zope.formlibwidget.browser.itemswidgets import MultiSelectFrozenSetWidget
from zope.formlibwidget.browser.itemswidgets import MultiCheckBoxWidget
from zope.formlibwidget.browser.itemswidgets import OrderedMultiSelectWidget

# Widgets that let you enter several items in a sequence
# These widgets are multi-views on (sequence type, value type)
from zope.formlibwidget.browser.sequencewidget import SequenceWidget
from zope.formlibwidget.browser.sequencewidget import TupleSequenceWidget
from zope.formlibwidget.browser.sequencewidget import ListSequenceWidget
from zope.formlibwidget.browser.sequencewidget import SequenceDisplayWidget

from zope.formlibwidget.browser.objectwidget import ObjectWidget
