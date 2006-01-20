
import datetime
import pytz

from zope.interface import implements
from zope.interface.common import idatetime

from zope.event import notify
from zope.security.interfaces import Unauthorized
from zope.app.exception.interfaces import UserError
from zope.app.traversing.interfaces import TraversalError

from zope.app import zapi
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.copypastemove.interfaces import IPrincipalClipboard
from zope.app.copypastemove.interfaces import IObjectCopier
from zope.app.copypastemove.interfaces import IObjectMover
from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.app.container.interfaces import DuplicateIDError

from zope.formlib import form
from zope.formlib.i18n import _

from zorg.table.browser.form import TableFormBase, RowFormBase
from zorg.table.browser.form import tableAction, rowAction
from zorg.table.browser.form import TableAction, RowAction
from zorg.table.browser.form import isFormDisplayMode, isFormEditMode
from zorg.table.browser.form import isRowDisplayMode, isRowEditMode


class RowForm(RowFormBase):    

    containerRow_actions = form.Actions()

    def actions():
        def _getActions(self):
            return (self.baseRow_actions + self.containerRow_actions)
        return property(_getActions)
    
    actions = actions()

    @rowAction("Apply", actions=containerRow_actions, condition=isRowEditMode)
    def handle_apply_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            notify(ObjectModifiedEvent(self.context))
            formatter = self.request.locale.dates.getFormatter(
                'dateTime', 'medium')

            try:
                time_zone = idatetime.ITZInfo(self.request)
            except TypeError:
                time_zone = pytz.UTC
                
            m = {'date_time':formatter.format(datetime.datetime.now(time_zone))}
            self.status = (_("Updated on ${date_time}", mapping=m),)
        else:
            self.status = (_('No changes'),)
        self.newmode = 'display'


def hasClipboardContents(form, action):
    """ interogates the `PrinicipalAnnotation` to see if
       clipboard contents exist """

    if not isFormDisplayMode(form, action):
        return False

    if not form.pasteable():
        return False

    # touch at least one item to in clipboard confirm contents
    clipboard = getPrincipalClipboard(form.request)
    items = clipboard.getContents()
    for item in items:
        try:
            zapi.traverse(form.context, item['target'])
        except TraversalError:
            pass
        else:
            return True

    return False


class TableForm(TableFormBase):

    container_actions = form.Actions()

    def actions():
        def _getActions(self):
            return (self.base_actions + self.container_actions)
        return property(_getActions)
    
    actions = actions()

    def rowForm(self, row, **kwargs):
        return RowForm(row, self.mode, **kwargs)
        
    def safe_getattr(self, obj, attr, default):
        """Attempts to read the attr, returning default if Unauthorized."""
        try:
            return getattr(obj, attr, default)
        except Unauthorized:
            return default

    def pasteable(self):
        """Decide if there is anything to paste."""
        target = self.context
        clipboard = getPrincipalClipboard(self.request)
        items = clipboard.getContents()
        for item in items:
            try:
                obj = zapi.traverse(target, item['target'])
            except TraversalError:
                pass
            else:
                if item['action'] == 'cut':
                    mover = IObjectMover(obj)
                    moveableTo = self.safe_getattr(mover, 'moveableTo', None)
                    if moveableTo is None or not moveableTo(target):
                        return False
                elif item['action'] == 'copy':
                    copier = IObjectCopier(obj)
                    copyableTo = self.safe_getattr(copier, 'copyableTo', None)
                    if copyableTo is None or not copyableTo(target):
                        return False
                else:
                    raise

        return True

    @tableAction("Edit", actions=container_actions, condition=isFormDisplayMode)
    def handle_edit_action(self, action, data):
        """edit objects specified in a list of object ids"""

        selected = False
        for form in self.forms.values():
            if form.row.selected:
                selected = True
                break
        if selected:
            self.newmode = 'edit'
        else:
            self.errors = (_("You didn't specify any ids to edit."),)

    @tableAction("Cut", actions=container_actions, condition=isFormDisplayMode)
    def handle_cut_action(self, action, data):
        """move objects specified in a list of object ids"""

        container_path = zapi.getPath(self.context)

        # For each item, check that it can be moved; if so, save the
        # path of the object for later moving when a destination has
        # been selected; if not movable, provide an error message
        # explaining that the object can't be moved.
        items = []
        for form in self.forms.values():
            if form.row.selected:
                id = form.row.key
                ob = form.context        
                mover = IObjectMover(ob)
                if not mover.moveable():
                    m = {"name": id}
                    title = getDCTitle(ob)
                    if title:
                        m["title"] = title
                        self.errors = (_(
                            "Object '${name}' (${title}) cannot be moved",
                            mapping=m),)
                    else:
                        self.errors = (_("Object '${name}' cannot be moved",
                                       mapping=m),)
                    return
                items.append(zapi.joinPath(container_path, id))

        if len(items) == 0:
            self.errors = (_("You didn't specify any ids to cut."),)
        else:
            # store the requested operation in the principal annotations:
            clipboard = getPrincipalClipboard(self.request)
            clipboard.clearContents()
            clipboard.addItems('cut', items)

    @tableAction("Copy", actions=container_actions, condition=isFormDisplayMode)
    def handle_copy_action(self, action, data):
        """Copy objects specified in a list of object ids"""

        container_path = zapi.getPath(self.context)

        # For each item, check that it can be copied; if so, save the
        # path of the object for later copying when a destination has
        # been selected; if not copyable, provide an error message
        # explaining that the object can't be copied.

        items = []
        for form in self.forms.values():
            if form.row.selected:
                id = form.row.key
                ob = form.context
                copier = IObjectCopier(ob)
                if not copier.copyable():
                    m = {"name": id}
                    title = getDCTitle(ob)
                    if title:
                        m["title"] = title
                        self.errors = (_(
                            "Object '${name}' (${title}) cannot be copied",
                            mapping=m),)
                    else:
                        self.errors = (_("Object '${name}' cannot be copied",
                                       mapping=m),)
                    return
                items.append(zapi.joinPath(container_path, id))

        if len(items) == 0:
            self.errors = (_("You didn't specify any ids to copy."),)
        else:
            # store the requested operation in the principal annotations:
            clipboard = getPrincipalClipboard(self.request)
            clipboard.clearContents()
            clipboard.addItems('copy', items)

    @tableAction("Paste", actions=container_actions, condition=hasClipboardContents)
    def handle_paste_action(self, action, data):
        """Paste ojects in the user clipboard to the container"""
        self.form_reset = True
        target = self.context
        clipboard = getPrincipalClipboard(self.request)
        items = clipboard.getContents()
        moved = False
        not_pasteable_ids = []
        for item in items:
            duplicated_id = False
            try:
                obj = zapi.traverse(target, item['target'])
            except TraversalError:
                pass
            else:
                if item['action'] == 'cut':
                    mover = IObjectMover(obj)
                    try:
                        mover.moveTo(target)
                        moved = True
                    except DuplicateIDError:
                        duplicated_id = True
                elif item['action'] == 'copy':
                    copier = IObjectCopier(obj)
                    try:
                        copier.copyTo(target)
                    except DuplicateIDError:
                        duplicated_id = True
                else:
                    raise

            if duplicated_id:
                not_pasteable_ids.append(zapi.getName(obj))                

        if moved:
            # Clear the clipboard if we do a move, but not if we only do a copy
            clipboard.clearContents()

        if not_pasteable_ids != []:
            # Show the ids of objects that can't be pasted because
            # their ids are already taken.
            # TODO Can't we add a 'copy_of' or something as a prefix
            # instead of raising an exception ?
            self.errors = (
                _("The given name(s) %s is / are already being used" %(
                str(not_pasteable_ids))),)

    @tableAction("Delete", actions=container_actions, condition=isFormDisplayMode)
    def handle_delete_action(self, action, data):
        """Delete objects specified in a list of object ids"""

        container = self.context

        selected = False
        for form in self.forms.values():
            if form.row.selected:
                id = form.row.key
                del container[id]
                selected = True

        if selected:
            self.form_reset = True
        else:
            self.errors = (_("You didn't specify any ids to delete."),)            

    @tableAction("Apply", actions=container_actions, condition=isFormEditMode)
    def handle_apply_action(self, action, data):
        self.handOverAction('apply', 'Apply')
        self.newmode = 'display'
        self.form_reset = True

    @tableAction("Cancel", actions=container_actions, condition=isFormEditMode)
    def handle_cancel_action(self, action, data):
        self.newmode = 'display'
        self.form_reset = True

        
def getDCTitle(ob):
    dc = IDCDescriptiveProperties(ob, None)
    if dc is None:
        return None
    else:
        return dc.title


def getPrincipalClipboard(request):
    """Return the clipboard based on the request."""
    user = request.principal
    annotationutil = zapi.getUtility(IPrincipalAnnotationUtility)
    annotations = annotationutil.getAnnotations(user)
    return IPrincipalClipboard(annotations)

