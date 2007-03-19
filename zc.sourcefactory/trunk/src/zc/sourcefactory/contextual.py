##############################################################################
#
# Copyright (c) 2006 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""The most basic source factory that supports context binding.

"""
__docformat__ = "reStructuredText"


import zc.sourcefactory.factories
import zc.sourcefactory.policies


class BasicContextualSourceFactory(
    zc.sourcefactory.factories.ContextualSourceFactory,
    zc.sourcefactory.policies.BasicContextualSourcePolicy):
    """Abstract base implementation for a basic contextual source factory."""
