##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

from zope.interface import Interface

class INonEmptyDirective(Interface):

    def __call__(context,**kw):
        """Compute subdirective handler

        context -- an execution context that the directive may use for
          things like resolving names

        kw -- a dictionary containing the values of any attributes
          that were specified on the directive

        Return an ISubdirectiveHandler.
        """

class IEmptyDirective(Interface):

    def __call__(context,**kw):
        """Compute configuration actions

        context -- an execution context that the directive may use for
          things like resolving names

        kw -- a dictionary containing the values of any attributes
          that were specified on the directive

        Return a sequence of configuration actions. Each action is a
        tuple with:

        - A discriminator, value used to identify conflicting
          actions. Actions conflict if they have the same values
          for their discriminators.

        - callable object

        - argument tuple

        - and, optionally, a keyword argument dictionary.

        The callable object will be called with the argument tuple and
        keyword arguments to perform the action.
        """


class ISubdirectiveHandler(Interface):
    """Handle subdirectives

    Provide methods for registered subdirectives. The methods are
    typically IEmptyDirective objects. They could, theoretically be
    INonEmptyDirective objects.

    Also provide a call that can provide additional configuration
    actions.

    """

    def __call__():
        """Return a sequence of configuration actions.

        See IEmptyDirective for a definition of configuration actions.

        This method should be called *after* any subdirective methods are
        called during the processing of the (sub)directive whose subdirectives
        are being processed.  It may return an empty list.
        """
