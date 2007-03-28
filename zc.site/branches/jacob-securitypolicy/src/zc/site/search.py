##############################################################################
#
# Copyright (c) 2003 Zope Corporation. All Rights Reserved.
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
"""
Search support classes.

These classes are used to support handling and presenting search
results.  Results must be sets of int ids.

"""
__docformat__ = "reStructuredText"

import zope.i18n
import zope.formlib.form
import zope.copypastemove.interfaces

from zope.app import zapi

import zc.readcatalog.utils
import zc.table.column

from zc.site.i18n import _


# Specialized column types

UNKNOWN_TYPE = _('unknown_type-title', 'Unknown')


class ReadStatusColumn(zc.table.column.SortingColumn):

    def renderCell(self, item, formatter):
        return zope.i18n.translate(
            zc.readcatalog.utils.readStatus(
                formatter.context.getObject(item), 
                formatter.request.principal.id))

    getSortKey = renderCell


class TypeColumn(zc.table.column.SortingColumn):

    types = () # types should be sequence of (interface, message
    # id) tuple pairs
    
    unknown_type = UNKNOWN_TYPE

    def __init__(self, title, types, name=None):
        self.types = types
        super(TypeColumn, self).__init__(title, name)

    def renderCell(self, item, formatter):
        obj = formatter.context.getObject(item)
        for i, msg in self.types:
            if i.providedBy(obj):
                return zope.i18n.translate(msg,
                                           default=msg,
                                           context=formatter.request)
        return zope.i18n.translate(self.unknown_type,
                                   context=formatter.request)

    getSortKey = renderCell


class SelectionColumn(zc.table.column.SelectionColumn):

    """Specialized selection column for use with search results.

    This provides a default idgetter implementation suitable for use
    with intids.

    """

    # It is important that the column selection provide only items that
    # are in the search results.  This ensures that security filters are
    # honored and that objects cannot be accessed simply by crafting a
    # request that references the int id of an object that should not be
    # referencable by the current user.

    # One expected improvement is to control whether the selection box
    # for each item is enabled or disabled based on whether the object
    # can be copied.

    def __init__(self, idgetter=None, field=None, prefix=None, getter=None,
                 setter=None, title=None, name='', hide_header=False):
        if idgetter is None:
            idgetter = lambda item: "%s_selected" % item
        super(SelectionColumn, self).__init__(
            idgetter, field=field, prefix=prefix,
            getter=getter, setter=setter, title=title, name=name,
            hide_header=hide_header)


# Action for use in forms:

class CopySelectionError(zope.app.form.interfaces.WidgetInputError):

    def __init__(self, msg):
        zope.app.form.interfaces.WidgetInputError.__init__(
            self, u"selected", u"Selected", msg)

    def doc(self):
        return self.errors

class UncopyableSelectionError(CopySelectionError):
    """Exception raised when an entry is selected that can't be copied."""

class NoItemsSelectedError(CopySelectionError):
    """Exception raised when no entry is selected for copying."""

    def __init__(self):
        CopySelectionError.__init__(
            self, _("No items selected for copying."))


class SelectionToClipboard(zope.formlib.form.Action):
    """Action that can copy selected items to the clipboard.

    The constructor needs to get the selection column that should be
    used as the basis for determining which items to copy.

    """

    def __init__(self, *args, **kw):
        """Initialize the action.

        Additional keyword arguments are accepted:

        `column` is the `SelectionColumn` that should be used as the
        selection discriminator.  This is required.

        `items` is a callable that should be used to get the set of
        items that needs to be passed to the selection column's
        `getSelected()` method.  The callable will be passed the form
        as an argument.  This is required.

        `key` is the key that should be used in the data dictionary.
        The default is 'selected-objects'.

        """
        self._selection_column = kw.pop("column")
        self._selection_name = kw.pop("key", "selected-objects")
        self._form_items = kw.pop("items")
        if not kw.get("label"):
            kw["label"] = _("zc-searchportlet-copy-selection-button",
                            default="Copy")
        if not kw.get("name"):
            kw["name"] = "copy"
        super(SelectionToClipboard, self).__init__(*args, **kw)

    def available(self):
        # Only show this action if there is anything to select from.
        items = self._form_items(self.form)
        if not items:
            return False
        it = iter(items)
        try:
            it.next()
        except StopIteration:
            return False
        else:
            return True

    def validate(self, data):
        """Check that selected objects can be copied.

        If any objects can't be copied, return
        UncopyableSelectionError instances for each.

        Add a list of selected, copyable objects to `data` using the
        key passed to the constructor.

        """
        items = []
        errors = []
        selected = self._selection_column.getSelected(
            self._form_items(self.form), self.form.request)

        for uid in selected:
            ob = self.form.getObject(uid)
            copier = zope.copypastemove.interfaces.IObjectCopier(ob)
            if copier.copyable():
                items.append(ob)
            else:
                m = {"name": ob.__name__}
                title = zope.app.container.browser.contents.getDCTitle(ob)
                if title:
                    msg = _(
                        "Object '${name}' (${title}) cannot be copied")
                    m["title"] = title
                else:
                    msg = _("Object '${name}' cannot be copied")
                msg.mapping.update(m)
                errors.append(UncopyableSelectionError(msg))
        data[self._selection_name] = items
        if not (errors or items):
            # No errors, but no items selected:
            errors.append(NoItemsSelectedError())
        return errors

    def success(self, data):
        """Copy the selected objects to the clipboard."""
        items = data[self._selection_name]
        clipboard = zope.app.container.browser.contents.getPrincipalClipboard(
            self.form.request)
        clipboard.clearContents()
        paths = [zapi.getPath(ob) for ob in items]
        clipboard.addItems('copy', paths)
        # Provide positive feedback that we've copied something;
        # `paths` will not be empty since `validate()` returns an
        # error in that case.
        if len(paths) == 1:
            self.form.status = _("One item copied to the clipboard.")
        else:
            self.form.status = _("${count} items copied to the clipboard.",
                                 mapping={"count": str(len(paths))})
