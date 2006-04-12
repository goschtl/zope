import datetime
import pytz
from zope.formlib.i18n import _
from zope.formlib import form
from zope.app.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.size.interfaces import ISized
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.location.interfaces import ILocation
from zope.event import notify
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.interface.common import idatetime
from zope.app import zapi
from zope.app.copypastemove.interfaces import IPrincipalClipboard
from zope.app.copypastemove.interfaces import IObjectCopier
from zope.app.copypastemove.interfaces import IObjectMover
from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.app.container.interfaces import DuplicateIDError
from zope.security.interfaces import Unauthorized
from zope.app.traversing.interfaces import TraversalError

from multiform import multiform, gridform
from multiform.interfaces import ISelection
from interfaces import IMovableLocation


def isSelected(form,action):
    return ISelection(form.context).selected

    
def isSelectedInput(form,action):
    print "isSelectedInput",form,form.inputMode,action.__name__,isSelected(form,action)
    if not form.inputMode:
        return False
    return isSelected(form,action)


def isSelectedOrDisplay(form,action):
    print "isSelectedOrDisplay",form.inputMode,isSelected(form,action)
    return not form.inputMode


def pasteable(containerForm):
    """Decide if there is anything to paste."""
    target = containerForm.context
    clipboard = getPrincipalClipboard(containerForm.request)
    items = clipboard.getContents()
    for item in items:
        try:
            obj = zapi.traverse(target, item['target'])
        except TraversalError:
            pass
        else:
            if item['action'] == 'cut':
                mover = IObjectMover(obj)
                moveableTo = safe_getattr(mover, 'moveableTo', None)
                if moveableTo is None or not moveableTo(target):
                    return False
            elif item['action'] == 'copy':
                copier = IObjectCopier(obj)
                copyableTo = safe_getattr(copier, 'copyableTo', None)
                if copyableTo is None or not copyableTo(target):
                    return False
            else:
                raise

    return True


def safe_getattr(obj, attr, default):
    """Attempts to read the attr, returning default if Unauthorized."""
    try:
        return getattr(obj, attr, default)
    except Unauthorized:
        return default


def hasClipboardContents(form, action):
    """ interogates the `PrinicipalAnnotation` to see if
       clipboard contents exist """

    if multiform.anySubFormInputMode(form,action):
        return False

    if not pasteable(form):
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


class ContainerItemForm(multiform.ItemFormBase):

    inputMode=False
    forceInput=['selected']
    template = ViewPageTemplateFile('griditem.pt')
    form_fields = form.Fields(ISelection['selected'],
                              IMovableLocation['__name__'],
                              IWriteZopeDublinCore['title'],
                        omit_readonly=False,render_context=True)

    @multiform.parentAction('Edit',
                            condition=multiform.allSubFormsDisplayMode)
    def handle_edit_action(self, action, data):
        #print "handle_edit_action",action,data,isSelected(self,action)
        if isSelected(self,action):
            self.newInputMode = True

    @multiform.parentAction("Save", inputMode=True,
                            condition=multiform.anySubFormInputMode)
    def handle_save_action(self, action, data):

        if not isSelected(self,action):
            return
        if form.applyChanges(self.context, self.form_fields,
                             data, self.adapters):
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
        ISelection(self.context).selected=False
        self.newInputMode = False
       

class ContainerGridForm(multiform.MultiFormBase):

    itemFormFactory=ContainerItemForm

    template = ViewPageTemplateFile('grid.pt')

    @form.action('Cancel',condition=multiform.anySubFormInputMode)
    def handle_cancel_action(self, action, data):
        for form in self.subForms.values():
            form.newInputMode = False

    @form.action("Paste", condition=hasClipboardContents)
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

    @form.action("Cut", condition=multiform.allSubFormsDisplayMode)
    def handle_cut_action(self, action, data):
        """move objects specified in a list of object ids"""

        container_path = zapi.getPath(self.context)

        # For each item, check that it can be moved; if so, save the
        # path of the object for later moving when a destination has
        # been selected; if not movable, provide an error message
        # explaining that the object can't be moved.
        items = []
        for form in self.getForms():
            ob = form.context
            name = ob.__name__
            selection = ISelection(ob)
            if not selection.selected:
                continue
            selection.selected=False
            mover = IObjectMover(ob)
            if not mover.moveable():
                m = {"name": name}
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
            items.append(zapi.joinPath(container_path, name))
        if len(items) == 0:
            self.errors = (_("You didn't specify any ids to cut."),)
        else:
            # store the requested operation in the principal annotations:
            clipboard = getPrincipalClipboard(self.request)
            clipboard.clearContents()
            clipboard.addItems('cut', items)

    @form.action("Copy", condition=multiform.allSubFormsDisplayMode)
    def handle_copy_action(self, action, data):
        """Copy objects specified in a list of object ids"""

        container_path = zapi.getPath(self.context)

        # For each item, check that it can be copied; if so, save the
        # path of the object for later copying when a destination has
        # been selected; if not copyable, provide an error message
        # explaining that the object can't be copied.

        items = []
        for form in self.getForms():
            ob = form.context
            name = ob.__name__
            selection = ISelection(ob)
            if not selection.selected:
                continue
            selection.selected=False
            copier = IObjectCopier(ob)
            if not copier.copyable():
                m = {"name": name}
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
            items.append(zapi.joinPath(container_path, name))
        if len(items) == 0:
            self.errors = (_("You didn't specify any ids to copy."),)
        else:
            # store the requested operation in the principal annotations:
            clipboard = getPrincipalClipboard(self.request)
            clipboard.clearContents()
            clipboard.addItems('copy', items)

    @form.action("Delete", condition=multiform.allSubFormsDisplayMode)
    def handle_delete_action(self, action, data):
        """Delete objects specified in a list of object ids"""
        container = self.context
        toDelete = []
        for form in self.getForms():
            if not ISelection(form.context).selected:
                continue
            toDelete.append(form.context.__name__)
        if toDelete:
            for name in toDelete:
                del(container[name])
            self.form_reset = True
        else:
            self.errors = (_("You didn't specify any ids to delete."),)            


def getPrincipalClipboard(request):
    """Return the clipboard based on the request."""
    user = request.principal
    annotationutil = zapi.getUtility(IPrincipalAnnotationUtility)
    annotations = annotationutil.getAnnotations(user)
    return IPrincipalClipboard(annotations)

