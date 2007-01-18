
import datetime
import pytz

from zope import component

from zope.interface.common import idatetime
from zope.app.i18n import ZopeMessageFactory as _
from zope.formlib import form
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app import zapi
from zope.copypastemove.interfaces import IPrincipalClipboard
from zope.copypastemove.interfaces import IObjectCopier
from zope.copypastemove.interfaces import IObjectMover
from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.app.container.interfaces import DuplicateIDError
from zope.app.container.browser.contents import getPrincipalClipboard, getDCTitle
from zope.app.form.browser import TextWidget, DisplayWidget
from zope.security.interfaces import Unauthorized
from zope.traversing.interfaces import TraversalError

from z3c.multiform import multiform, gridform
from z3c.multiform.interfaces import ISelection
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


def condition_paste_action(form, action):
    return hasClipboardContents(form, action)
label_paste_action = _("container-paste-button")

def condition_cut_action(form, action):
    return multiform.allSubFormsDisplayMode(form, action)
label_cut_action = _("container-cut-button")

def condition_copy_action(form, action):
    return multiform.allSubFormsDisplayMode(form, action)
label_copy_action = _("container-copy-button")
 
def condition_delete_action(form, action):
    return multiform.allSubFormsDisplayMode(form, action)
label_delete_action = _("container-delete-button")

def condition_cancel_action(form, action):
    return multiform.anySubFormInputMode(form, action)
label_cancel_action = _('Cancel')


class ContainerActions(object):
    
    def handle_cancel_action(self, action, data):
        for form in self.subForms.values():
            form.newInputMode = False

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

    def handle_cut_action(self, action, data):
        """move objects specified in a list of object ids"""

        container_path = zapi.getPath(self.context)

        # For each item, check that it can be moved; if so, save the
        # path of the object for later moving when a destination has
        # been selected; if not movable, provide an error message
        # explaining that the object can't be moved.
        items = []
        for key in self.forms:
            ob = self.subForms[key].context
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

    def handle_copy_action(self, action, data):
        """Copy objects specified in a list of object ids"""

        container_path = zapi.getPath(self.context)

        # For each item, check that it can be copied; if so, save the
        # path of the object for later copying when a destination has
        # been selected; if not copyable, provide an error message
        # explaining that the object can't be copied.

        items = []
        for key in self.forms:
            ob = self.subForms[key].context
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

    def handle_delete_action(self, action, data):
        """Delete objects specified in a list of object ids"""
        toDelete = []
        for key in self.forms:
            ob = self.subForms[key].context
            if not ISelection(ob).selected:
                continue
            toDelete.append(ob)
        if toDelete:
            for ob in toDelete:
                container = ob.__parent__
                if container is not None:
                    del container[ob.__name__]
            self.form_reset = True
        else:
            self.errors = (_("You didn't specify any ids to delete."),)            

def condition_edit_action(form, action):
    return multiform.allSubFormsDisplayMode(form, action)
label_edit_action = _("Edit")

def condition_save_action(form, action):
    return multiform.anySubFormInputMode(form, action)
label_save_action = _("Save")


class ContainerItemActions(object):

    def handle_edit_action(self, action, data):
        if isSelected(self,action):
            self.newInputMode = True

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
       

class NameTextWidget(TextWidget):

    def __call__(self):
        content = super(NameTextWidget, self).__call__()
        # bad!
        context = self.context.context.context
        # zmi icon
        zmi_icon = component.queryMultiAdapter((context, self.request), name='zmi_icon')        
        if zmi_icon is not None:
            icon = u'<img class="itemicon" src="%s" />&nbsp;' % zmi_icon.url()
        else:
            icon = u''
        return icon + content


class NameDisplayWidget(DisplayWidget):
    
    def __call__(self):
        content = super(NameDisplayWidget, self).__call__()
        # bad!
        context = self.context.context.context
        # zmi icon
        zmi_icon = component.queryMultiAdapter((context, self.request), name='zmi_icon')        
        if zmi_icon is not None:
            icon = u'<img class="itemicon" src="%s" />&nbsp;' % zmi_icon.url()
        else:
            icon = u''
        # link
        url = zapi.absoluteURL(context, self.request)
        result = u'<a href="%s/@@SelectedManagementView.html">%s%s</a>' % (url, icon, content)
        return result

    
class ContainerItemForm(multiform.ItemFormBase,
                        ContainerItemActions):

    inputMode=False
    forceInput=['selected']
    template = ViewPageTemplateFile('griditem.pt')
    form_fields = form.Fields(ISelection['selected'],
                              IMovableLocation['__name__'],
                              IWriteZopeDublinCore['title'],
                              IWriteZopeDublinCore['created'],
                              IWriteZopeDublinCore['modified'],
                        omit_readonly=False,render_context=True)
    form_fields['created'].for_display=True
    form_fields['modified'].for_display=True
    form_fields['__name__'].custom_widget=multiform.MultiformWidgets(
                         NameTextWidget, NameDisplayWidget)

    actions = form.Actions(
           multiform.ParentAction(label_edit_action,
                                  success='handle_edit_action',
                                  condition=condition_edit_action),
           multiform.ParentAction(label_save_action,
                                  inputMode=True,
                                  success='handle_save_action',
                                  condition=condition_save_action)
           )
                         

class ContainerGridForm(multiform.MultiFormBase,
                        ContainerActions):

    itemFormFactory=ContainerItemForm

    template = ViewPageTemplateFile('grid.pt')

    actions = form.Actions(
       form.Action(label_cancel_action,
                   success='handle_cancel_action',
                   condition=condition_cancel_action),
       form.Action(label_paste_action,
                   success='handle_paste_action',
                   condition=condition_paste_action),
       form.Action(label_cut_action,
                   success='handle_cut_action',
                   condition=condition_cut_action),
       form.Action(label_copy_action,
                   success='handle_copy_action',
                   condition=condition_copy_action),
       form.Action(label_delete_action,
                   success='handle_delete_action',
                   condition=condition_delete_action)
       )


class ContainerItemIndexForm(multiform.ItemFormBase):

    inputMode=False
    template = ViewPageTemplateFile('griditem.pt')
    form_fields = form.Fields(IMovableLocation['__name__'],
                              IWriteZopeDublinCore['title'],
                              IWriteZopeDublinCore['created'],
                              IWriteZopeDublinCore['modified'],
                        omit_readonly=False,render_context=True)
    form_fields['created'].for_display=True
    form_fields['modified'].for_display=True
    form_fields['__name__'].custom_widget=NameDisplayWidget

    
class ContainerIndexForm(multiform.MultiFormBase):

    itemFormFactory=ContainerItemIndexForm

    template = ViewPageTemplateFile('grid.pt')

