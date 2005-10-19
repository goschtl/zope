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
from zope.app.publisher.interfaces.browser import IBrowserView
from zope.component.interfaces import IView
from zope import interface, schema
from zope.subview.i18n import _

# XXX try to reconcile with zope.formlib.interfaces.ISubPage: I hope to
# remove setPrefix from that interface, and ideally add parent and name,
# to that interface.  That will take discussion.  If that happens, then 
# I'd like to try to import ISubPage and declare ISubview to extend ISubPage
# if the formlib package exists.

class IIdentifiedViewComponent(interface.Interface):

    identifier = schema.DottedName(
        # XXX!!! W3C validator reportedly doesn't like
        # our dotted ids.  Neither Fred nor I can find why in the XHTML or
        # HTML or XML specs, so need to replicate in the validator and see if
        # it has more information.  Many other separators should work, but
        # dots feel natural from a Python perspective.
        title=_('Identifier'), description=_(
        """An identifier.  Should be unique among all identifiers used for a
        view in a given request.  Should be used as a prefix for view ids.
        The view component must not use the prefix directly for any names or
        ids in the rendered output: it is reserved by containing/calling
        views, if any.  The prefix should be used with a following dot ('.')
        for all identifiers within the view component--that is, if a prefix is
        'form', then names and ids within the associated view should all begin
        with 'form.', like 'form.title'.""",
        readonly=True, required=True)

class IStagedView(IView):
    """A view that must have `update` called before `__call__`.  Any contained
    (or managed) subviews must also have `update` called before any view or
    subview is rendered with __call__"""

    def __call__():
        """render; should (but not required) raise informative error if called 
        before update

        (see update)"""

    def update():
        """Initialize view; perform all state calculation here, not in render.
        
        In this method, all state must be calculated from the current
        interaction (e.g., the browser request); all contained or managed
        IStagedViews must have update called; any additional stateful API
        for contained or managed subviews must be handled; and persistent
        objects should be modified, if the view is going to do it.  Do
        *not* store state about persistent objects: render should actually use
        the persistent objects for the data, in case other components modify
        the object between the update and render stages.

        Initialize must be called before any other method that mutates the
        instance (besides __init__).  Non mutating methods and attributes may
        raise an error if used before calling update.  View may rely on
        this order but is not required to explicitly enforce this. 
        Implementations may enforce it as a developer aid.
        """

class IBrowserSubview(IBrowserView, IStagedView, IIdentifiedViewComponent):
    """A view that does not render a full page, but part of a page."""
    

    def update(parent=None, name=None, state=None):
        """All of IStagedView.update, plus optionally set prefix and state.

        parent and name must be set before this method is called, or
        they must be passed in (as the parent and name arguments,
        respectively) and set initially by this method.  See the attributes for
        more detail.  parent and name may be set independently of this method,
        such as between update and render, if state calculation should
        be performed in one context, and rendering in another.

        The subview will try to get its state from the environment (e.g., the
        context and request), using the prefix, if any. The state will be used
        to try to reinitialize the subview's user-visible state.
        
        If this subview is a subview container, it is responsible for calling 
        update on all directly contained subviews when update is
        called (*not* postponed to render).
        
        XXX state
        """

    __parent__ = interface.Attribute(
        """The ISubviewCollection that contains this view.  Required.""")

    __name__ = schema.DottedName(
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

    identifier = schema.DottedName(
        title=_('Identifier'), description=_(
        """See IIdentifiedViewComponent.prefix.  Must be calculated.
        Identifier must be one of two types.

        One choice is a hierarchically derived combination of the parent's
        identifier value joined by a dot ('.') to the name.  For instance, if
        the parent's prefix were 'left_slot.form' and the current name were
        'title', then the prefix would be 'left_slot.form.title'.

        The other choice is a guaranteed unique and consistent name, as
        determined by the subview author, following a prescribed formula: the
        reserved initial prefix of 'zope.subview.', plus the path to the
        package of the code that is guaranteeing the unique ids, plus the
        unique id.  For instance, if a zc.portlet package used the intid
        utility to provide unique names, and the intid of the view's underlying
        portlet object were 13576, the prefix might be
        'zope.subview.zc.portlet.13576'.
        
        Note that this subview might itself be a parent to another subview
        that got its prefix via the hierarchical combination; if its name were
        'title' then its prefix would be zope.subview.zc.portlet.13576.title.
        
        Note also that a package may want to offer multiple namespaces, so
        zc.portlet might have zc.portlet.config and zc.portlet.view.""",
        readonly=True, required=True)

    def getState():
        """XXX
        
        None==no state."""

    def hasBrowserState():
        """XXX Needed to know when to initialize subviews.
        """

class ISubviewCollection(IIdentifiedViewComponent):
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

    identifier = schema.DottedName(
        title=_('Identifier'), description=_(
        """See IIdentifiedViewComponent.identifier.  If this is not also an ISubview,
        then this value is writable.""", readonly=False, required=True)
        
    def update():
        """Initialize all contained subviews: perform all state calculation.
        """

class IIntermediateSubview(ISubview, ISubviewCollection):
    """A subview that may contain nested subviews.  Note that initialize is
    readonly, like ISubview and IIdentifiedViewComponent, but different from
    ISubviewCollection"""
    
    def getBrowserState():
        """Returns persistent object.
        
        Should include state of contained subviews.
        """

    def update(parent=None, name=None, browserstate=None):
        """browserstate, if given, should contain state of contained subviews
        """
