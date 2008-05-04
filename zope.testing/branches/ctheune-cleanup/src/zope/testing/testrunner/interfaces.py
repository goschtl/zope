##############################################################################
#
# Copyright (c) 2004-2008 Zope Corporation and Contributors.
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
"""Test runner interfaces

XXX Note: These interfaces are still being sketched out. Please do not rely on
them, yet.

$Id: __init__.py 86232 2008-05-03 15:09:33Z ctheune $

"""

import zope.interface


class IFeature(zope.interface.Interface):
    """Features extend the test runners functionality in a pipe-lined
    order.
    """

    def global_setup():
        """Executed once when the test runner is being set up."""

    def late_setup():
        """Executed once right before the actual tests get executed and after
        all global setups have happened.

        Should do as little work as possible to avoid timing interferences
        with other features.

        It is guaranteed that the calling stack frame is not left until
        early_teardown was called.

        """

    def test_setup():
        """Executed once before each test."""

    def test_teardown():
        """Executed once after each test."""

    def early_teardown():
        """Executed once directly after all tests.

        This method should do as little as possible to avoid timing issues.

        It is guaranteed to be called directly from the same stack frame that
        called `late_setup`.

        """

    def global_teardown():
        """Executed once after all tests where run and early teardowns have
        happened.

        """

    def report():
        """Executed once after all tests have been run and all setup was
        teared down.

        This is the only method that should produce output.

        """


class ITestRunner(zope.interface.Interface):
    """The test runner manages test layers and their execution.

    The functionality of a test runner can be extended by configuring
    features.

    """

    options = zope.interface.Attribute(
      "Provides access to configuration options.")
