##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Subview interfaces

$Id$
"""

from zope.component.interfaces import IView
from zope import interface, schema
from zope.subview.i18n import _

# XXX try to reconcile with zope.formlib.interfaces.ISubPage: I hope to
# remove setPrefix from that interface, and ideally add parent and name,
# to that interface.  That will take discussion.  If that happens, then 
# I'd like to try to import ISubPage and declare ISubview to extend ISubPage
# if the formlib package exists.

class IPrefixedView(IView):

    prefix = schema.DottedName(
        title=_('Prefix'), description=_(
        """A prefix for view ids, uniquely identifying the element among the
        view and any of its contained subviews.  The view must not use the
        prefix directly for any names or ids: it is reserved by containing/calling
        views, if any.  The prefix should be used with a following dot ('.')
        for all identifiers within the view--that is, if a prefix is 'form',
        then names and ids within the associated view should all begin with
        'form.', like 'form.title'.""",
        readonly=True, required=True)

class ISubview(IPrefixedView):
    """A view that does not render a full page, but part of a page."""
    
    def render():
        """render subview; should (but not required) raise error if called 
        before update

        (see update)"""

    def update(parent=None, name=None):
        """Initialize subview: perform all state calculation here, not in render).

        Initialize must be called before any other method that mutates the
        instance (besides __init__).  Non mutating methods and attributes may
        raise an error if used before calling update.  Subview may rely on
        this order but are not required to explicitly enforce this. 
        Implementations may enforce it as a developer aid.

        parent and name must be set before this method is called, or
        they must be passed in (as the parent and name arguments,
        respectively) and set initially by this method.  See the attributes for
        more detail.  parent and name may be set independently of this method,
        such as between update and render, if state calculation should
        be performed in one context, and rendering in another.

        The subview will try to get its state from the environment (e.g., the
        context and request), using the prefix, if any. The state will be used
        to try to reinitialize the subview's user-visible state.

        In order to facilitate non-stateless interactions, update
        must be able to be called more than once on the same subview instance.
        Each call should recalculate the subview state on the basis of the new
        arguments.
        
        If this subview is a subview container, it is responsible for calling 
        update on all directly contained subviews when update is
        called (*not* postponed to render).
        """

    parent = interface.Attribute(
        """The ISubviewCollection that contains this view.  Required.""")

    name = schema.DottedName(
        title=_('Name'), description=_(
        """The name by which this subview may be obtained from its __parent__
        via getSubview.  Subviews may suggest values but must be amenable
        to having the suggestions overridden.  Suggested values, if any, must
        be stable across renderings and transactions.
        
        Concurrency issues suggest that you should often avoid reusing subview
        names (that is, having names refer to one subview and then another)
        within a given logical set of renderings of a subview.
        """),
        min_dots=0, max_dots=0, required=True)

    prefix = schema.DottedName(
        title=_('Prefix'), description=_(
        """See IPrefixedView.prefix.  Must be calculated.  Prefix must be one
        of two types.

        One choice is a hierarchically derived combination of the parent's
        prefix value joined by a dot ('.') to the name.  For instance, if the
        parent's prefix were 'left_slot.form' and the current name were
        'title', then the prefix would be 'left_slot.form.title'.

        The other choice is a guaranteed unique and consistent name, as
        determined by the subview author, following a prescribed formula: the
        reserved initial prefix of 'zope.subview.', plus the path to the
        package of the code that is providing the unique ids, plus the unique
        id.  For instance, if someone used the intid utility to provide unique
        names, and the intid of the current view were 13576, the prefix might
        be 'zope.subview.zope.app.intid.13576'.  Note that this subview might
        itself be a parent to another subview that got its prefix via the
        hierarchical combination; if its name were 'title' then its prefix
        would be zope.subview.zope.app.intid.13576.title""", readonly=True,
        required=True)

class IPersistentSubview(ISubview):
    """Must also implement IPersistent.  However, requests, contexts, and
    non-IPersistent parents *must not be persisted*.  (Requests and security
    wrappers around contexts are not persistable, and non-persistent parents
    are not designed to be persistent and so may themselves contain references
    to requests, contexts, or other problematic values.)"""

class ISubviewCollection(IPrefixedView):
    """Collection of subviews, geared towards iterating over subviews and
    finding specific subviews by name.

    To enable replacement of individual subviews on a page through technologies
    such as AJAX, and to enable drag and drop approaches within subviews, 
    subview collections must enclose the rendered output of each
    directly contained subview within a div block with an id of the subview's
    prefix and a class of "zope.subview".
    """

    def iterSubviews():
        """return an iterator of pairs of (name, subview) for all directly
        contained subviews."""

    def getSubview(name):
        """given a name, return the directly contained subview, or None if not
        found."""

    def getSubviewByPrefix(prefix):
        """return the (nested) subview matching the given prefix, or None.
        """

    prefix = schema.DottedName(
        title=_('Prefix'), description=_(
        """See IPrefixedView.prefix.  If this is not also an ISubview,
        then this value is writable.""", readonly=False, required=True)
        
    def update():
        """Initialize all contained subviews: perform all state calculation.
        """

class IPersistentSubviewCollection(ISubviewCollection):
    """Implements IPersistent.    However, requests and contexts *must not be
    persisted*.  (Requests and security wrappers around contexts are not
    persistable.)
    
    Any contained subview must implement IPersistentSubview (including
    IPersistentIntermediateSubview, which extends IPersistentSubview).
    """

class IIntermediateSubview(ISubview, ISubviewCollection):
    """A subview that may contain nested subviews.  Note that prefix is
    readonly, like ISubview and IPrefixedView, but different from
    ISubviewCollection"""

class IPersistentIntermediateSubview(
    IPersistentSubview, IPersistentSubviewCollection, IIntermediateSubview):
    """Implements IPersistent.  However, requests, contexts, and
    non-IPersistent parents *must not be persisted*.  (Requests and security
    wrappers around contexts are not persistable, and non-persistent parents
    are not designed to be persistent and so may themselves contain references
    to requests, contexts, or other problematic values.)
    
    Any contained subview must implement IPersistentSubview (including
    IPersistentIntermediateSubview, which extends IPersistentSubview).
    """
