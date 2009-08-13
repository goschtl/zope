"""Formlib based view for folders
$Id$"""

import urllib

from ZTUtils import Batch
from ZTUtils import LazyFilter
from ZTUtils import make_query
from DocumentTemplate import sequence

from zope.interface import Interface, directlyProvides
from zope import schema
from zope.schema import Bool, TextLine, Int, Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.interfaces import IDynamicType

from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.exceptions import zExceptions_Unauthorized
from Products.CMFDefault.permissions import ListFolderContents
from Products.CMFDefault.permissions import ManageProperties
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.formlib.form import ContentEditFormBase

from utils import ViewBase
from utils import decode
from utils import memoize

import logging
LOG = logging.getLogger("formlib for folders")

def contents_delta_vocabulary(context):
    """Vocabulary for the pulldown for moving objects up
    and down."""
    length = len(context.contentIds())
    deltas = [SimpleTerm(i, str(i), str(i)) 
            for i in range(1, min(5, length)) + range(5, length, 5)]
    return SimpleVocabulary(deltas)


class IFolderItem(Interface):
    """Schema for folderish objects contents."""
    
    select = Bool(
        required=False)
        
    name = TextLine(
        title=u"Name",
        required=False,
        readonly=True)


class IDeltaItem(Interface):
    """Schema for delta"""    
    delta = Choice(
        title=u"By",
        description=u"Move an object up or down the chosen number of places.",
        required=False,
        vocabulary=u'cmf.contents delta vocabulary',
        default=1)

        
class IHidden(Interface):
    """Schema for hidden items"""
    
    b_start = Int(
        title=u"Batch start",
        required=False)
        
    key = TextLine(
        title=u"Sort key",
        required=False)
        
    reverse = Bool(
        title=u"Reverse sort order",
        required=False)


class BatchViewBase(ViewBase):

    """Helper class for creating batch-based views."""

    _BATCH_SIZE = 25

    @memoize
    def _getBatchStart(self):
        return int(self.request.form.get('b_start', 0))

    @memoize
    def _getBatchObj(self):
        b_start = self._getBatchStart()
        items = self._get_items()
        return Batch(items, self._BATCH_SIZE, b_start, orphan=0)

    @memoize
    def _getHiddenVars(self):
        return {}

    @memoize
    def _getNavigationVars(self):
        return self._getHiddenVars()

    @memoize
    def _getNavigationURL(self, b_start):
        target = self._getViewURL()
        kw = self._getNavigationVars().copy()

        kw['b_start'] = b_start
        for k, v in kw.items():
            if not v or k == 'portal_status_message':
                del kw[k]

        query = kw and ('?%s' % make_query(kw)) or ''
        return u'%s%s' % (target, query)

    # interface

    @memoize
    @decode
    def listBatchItems(self):
        batch_obj = self._getBatchObj()
        portal_url = self._getPortalURL()

        items = []
        for item in batch_obj:
            item_description = item.Description()
            item_icon = item.getIcon(1)
            item_title = item.Title()
            item_type = remote_type = item.Type()
            if item_type == 'Favorite' and not item_icon == 'p_/broken':
                item = item.getObject()
                item_description = item_description or item.Description()
                item_title = item_title or item.Title()
                remote_type = item.Type()
            is_file = remote_type in ('File', 'Image')
            is_link = remote_type == 'Link'
            items.append({'description': item_description,
                          'format': is_file and item.Format() or '',
                          'icon': item_icon and ('%s/%s' %
                                               (portal_url, item_icon)) or '',
                          'size': is_file and ('%0.0f kb' %
                                            (item.get_size() / 1024.0)) or '',
                          'title': item_title,
                          'type': item_type,
                          'url': is_link and item.getRemoteUrl() or
                                 item.absolute_url()})
        return tuple(items)

    @memoize
    def navigation_previous(self):
        batch_obj = self._getBatchObj().previous
        if batch_obj is None:
            return None

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Previous item')
        else:
            title = _(u'Previous ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    @memoize
    def navigation_next(self):
        batch_obj = self._getBatchObj().next
        if batch_obj is None:
            return None

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Next item')
        else:
            title = _(u'Next ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    def page_range(self):
        """Create a range of up to ten pages around the current page"""
        url = self._getViewURL()
        batch_query = '%s?b_start:int=%s'
        pages = [(idx + 1, b_start) for idx, b_start in enumerate(
                    range(0, 
                        self._getBatchObj().sequence_length, 
                        self._BATCH_SIZE)
                    )
                ]
        range_start = max(self.page_number() - 5, 0)
        range_stop = min(max(self.page_number() + 5, 10), len(pages))
        _page_range = []
        for page, b_start in pages[range_start:range_stop]:
            _page_range.append({'number':page, 
            'url':batch_query % (url, b_start)})
        return _page_range

    @memoize
    def page_count(self):
        """Count total number of pages in the batch"""
        batch_obj = self._getBatchObj()
        count = (batch_obj.sequence_length - 1) / self._BATCH_SIZE + 1
        return count

    @memoize
    def page_number(self):
        """Get the number of the current page in the batch"""
        return (self._getBatchStart() / self._BATCH_SIZE) + 1

    @memoize
    def summary_length(self):
        length = self._getBatchObj().sequence_length
        return length and thousands_commas(length) or ''

    @memoize
    def summary_type(self):
        length = self._getBatchObj().sequence_length
        return (length == 1) and _(u'item') or _(u'items')

    @memoize
    @decode
    def summary_match(self):
        return self.request.form.get('SearchableText')       


class ContentsView(BatchViewBase, ContentEditFormBase):
    """Folder contents view"""
    
    template = ViewPageTemplateFile('templates/contents.pt')
    
    object_actions = form.Actions(
        form.Action(
            name='rename',
            label=_(u'Rename'),
            validator='validate_items',
            condition='has_subobjects',
            success='handle_rename'),
        form.Action(
            name='cut',
            label=_(u'Cut'),
            condition='has_subobjects',
            validator='validate_items',
            success='handle_cut'),
        form.Action(
            name='copy',
            label=_(u'Copy'),
            condition='has_subobjects',
            validator='validate_items',
            success='handle_copy'),
        form.Action(
            name='paste',
            label=_(u'Paste'),
            condition='check_clipboard_data',
            success='handle_paste'),
        form.Action(
            name='delete',
            label=_(u'Delete'),
            condition='has_subobjects',
            validator='validate_items',
            success='handle_delete')
            )
            
    delta_actions = form.Actions(
        form.Action(
            name='up',
            label=_(u'Up'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_up'),
        form.Action(
            name='down',
            label=_(u'Down'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_down')
            )
            
    absolute_actions = form.Actions(
        form.Action(
            name='top',
            label=_(u'Top'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_top'),
        form.Action(
            name='bottom',
            label=_(u'Bottom'),
            condition='is_orderable',
            validator='validate_items',
            success='handle_bottom')
            )

    sort_actions = form.Actions(
        form.Action(
            name='sort_order',
            label=_(u'Set as Default Sort'),
            condition='can_sort_be_changed',
            validator='validate_items',
            success='handle_top')
            )
            
    actions = object_actions + delta_actions + absolute_actions + sort_actions
    errors = ()
    
    def __init__(self, *args, **kw):
        super(ContentsView, self).__init__(*args, **kw)
        self.hidden_fields = form.FormFields(IHidden)
        self.form_fields = form.FormFields()
        self.delta_field = form.FormFields(IDeltaItem)
        self.contents = self.context.contentValues()
        
        for item in self.contents:
            for name, field in schema.getFieldsInOrder(IFolderItem):
                field = form.FormField(field, name, item.id)
                self.form_fields += form.FormFields(field)

    @memoize
    @decode
    def up_info(self):
        """Link to the contens view of the parent object"""
        up_obj = self.context.aq_inner.aq_parent
        mtool = self._getTool('portal_membership')
        allowed = mtool.checkPermission(ListFolderContents, up_obj)
        if allowed:
            if IDynamicType.providedBy(up_obj):
                up_url = up_obj.getActionInfo('object/folderContents')['url']
                return {'icon': '%s/UpFolder_icon.gif' % self._getPortalURL(),
                        'id': up_obj.getId(),
                        'url': up_url}
            else:
                return {'icon': '',
                        'id': 'Root',
                        'url': ''}
        else:
            return {}
        
    def setUpWidgets(self, ignore_request=False):
        """Create widgets for the folder contents."""
        data = {}
        for i in self.contents:
            data['%s.name' %i.id] = i.getId()
        self.hidden_widgets = form.setUpDataWidgets(
                self.hidden_fields, "", self.context,
                self.request, data=self._getHiddenVars(),
                        ignore_request=ignore_request)
        self.widgets = form.setUpDataWidgets(
                self.form_fields, self.prefix, self.context,
                self.request, data=data, ignore_request=ignore_request)
        self.widgets += form.setUpDataWidgets(
                self.delta_field, self.prefix, self.context,
                self.request, ignore_request=ignore_request)
                
    @memoize
    def _get_sorting(self):
        """How should the contents be sorted"""
        key = self.request.form.get('key', None)
        if key:
            return (key, self.request.form.get('reverse', 0))
        else:
            return self.context.getDefaultSorting()
            
    @memoize
    def _is_default_sorting(self):
        return self._get_sorting() == self.context.getDefaultSorting()
    
    @memoize
    def column_headings(self):
        key, reverse = self._get_sorting()
        columns = ( {'key': 'Type',
                     'title': _(u'Type'),
                     'colspan': '2'}
                  , {'key': 'getId',
                     'title': _(u'Name')}
                  , {'key': 'modified',
                     'title': _(u'Last Modified')}
                  , {'key': 'position',
                     'title': _(u'Position')}
                  )
        for column in columns:
            if key == column['key'] and not reverse and key != 'position':
                query = make_query(key=column['key'], reverse=1)
            else:
                query = make_query(key=column['key'])
            column['url'] = '%s?%s' % (self._getViewURL(), query)
        return tuple(columns)
        
    @memoize
    def _get_items(self):
        (key, reverse) = self._get_sorting()
        items = self.contents
        return sequence.sort(items,
                             ((key, 'cmp', reverse and 'desc' or 'asc'),))
    
    @memoize
    def listBatchItems(self):
        """Return the widgets for the form in the interface field order"""
        batch_obj = self._getBatchObj()
        b_start = self._getBatchStart()
        key, reverse = self._get_sorting()
        fields = []

        for idx, item in enumerate(batch_obj):
            field = {'ModificationDate':item.ModificationDate()}
            field['select'] = self.widgets['%s.select' % item.getId()]
            field['name'] = self.widgets['%s.name' % item.getId()]
            field['url'] = item.absolute_url()
            field['title'] = item.TitleOrId()
            field['icon'] = item.icon
            field['position'] = (key == 'position') \
                                and str(b_start + idx + 1) \
                                or '...'
            field['type'] = item.Type() or None
            fields.append(field.copy())
        return fields
                
    def _get_ids(self, data):
        """Identify objects that have been selected"""
        ids = [k.split(".")[0] for k, v in data.items() 
                            if v is True \
                            and k.split(".")[-1] == 'select']
        return ids

    @memoize    
    def _getHiddenVars(self):
        b_start = self._getBatchStart()
        is_default = self._is_default_sorting()
        (key, reverse) = is_default and ('', 0) or self._get_sorting()
        return {'b_start': b_start, 'key': key, 'reverse': reverse}
    
    #Action conditions
    @memoize
    def has_subobjects(self, action=None):
        """Return false if the user cannot rename subobjects"""
        return bool(self.contents)
    
    @memoize
    def check_clipboard_data(self, action=None):
        """Any data in the clipboard"""
        return bool(self.context.cb_dataValid())
    
    @memoize
    def can_sort_be_changed(self, action=None):
        """Returns true if the default sort key may be changed 
            may be sorted for display"""
        items_move_allowed = self._checkPermission(ManageProperties)
        return items_move_allowed and not \
            self._get_sorting() == self.context.getDefaultSorting()

    @memoize
    def is_orderable(self, action=None):
        """Returns true if the displayed contents can be
            reorded."""
        (key, reverse) = self._get_sorting()        
        return key == 'position' and len(self.contents) > 1
    
    #Action validators
    def validate_items(self, action=None, data=None):
        """Check whether any items have been selected for 
        the requested action."""
        super(ContentsView, self).validate(action, data)
        if data is None or data == {}:
            return [_(u"Please select one or more items first.")]
        else:
            return []
            
    #Action handlers
    def handle_rename(self, action, data):
        """Redirect to rename view passing the ids of objects to be renamed"""
        # currently redirects to a PythonScript
        # should be replaced with a dedicated form
        self.request.form['ids'] = self._get_ids(data)
        keys = ",".join(self._getHiddenVars().keys() + ['ids'])
        # keys = 'b_start, ids, key, reverse'
        return self._setRedirect('portal_types', 'object/rename_items', keys)
        
    def handle_cut(self, action, data):
        """Cut the selected objects and put them in the clipboard"""
        ids = self._get_ids(data)
        try:
            self.context.manage_cutObjects(ids, self.request)
            if len(ids) == 1:
                self.status = _(u'Item cut.')
            else:
                self.status = _(u'Items cut.')
        except CopyError:
            self.status = _(u'CopyError: Cut failed.')
        except zExceptions_Unauthorized:
            self.status = _(u'Unauthorized: Cut failed.')
        return self._setRedirect('portal_types', 'object/new_contents')    

    def handle_copy(self, action, data):
        """Copy the selected objects to the clipboard"""
        ids = self._get_ids(data)
        try:
            self.context.manage_copyObjects(ids, self.request)
            if len(ids) == 1:
                self.status = _(u'Item copied.')
            else:
                self.status = _(u'Items copied.')
        except CopyError:
            self.status = _(u'CopyError: Copy failed.')
        return self._setRedirect('portal_types', 'object/new_contents')
    
    def handle_paste(self, action, data):
        """Paste the objects from the clipboard into the folder"""
        try:
            result = self.context.manage_pasteObjects(self.request['__cp'])
            if len(result) == 1:
                self.status = _(u'Item pasted.')
            else:
                self.status = _(u'Items pasted.')
        except CopyError, error:
            self.status = _(u'CopyError: Paste failed.')
            self.request['RESPONSE'].expireCookie('__cp', 
                    path='%s' % (self.request['BASEPATH1'] or "/"))

        except zExceptions_Unauthorized:
            self.status = _(u'Unauthorized: Paste failed.')
        return self._setRedirect('portal_types', 'object/new_contents')

    def handle_delete(self, action, data):
        """Delete the selected objects"""
        ids = self._get_ids(data)
        self.context.manage_delObjects(list(ids))
        if len(ids) == 1:
            self.status = _(u'Item deleted.')
        else:
            self.status = _(u'Items deleted.')
        return self._setRedirect('portal_types', 'object/new_contents')
    
    def handle_up(self, action, data):
        """Move the selected objects up the selected number of places"""
        ids = self._get_ids(data)
        delta = data.get('delta', 1)
        subset_ids = [obj.getId()
                       for obj in self.context.listFolderContents()]
        try:
            attempt = self.context.moveObjectsUp(ids, delta,
                                                 subset_ids=subset_ids)
            if attempt == 1:
                self.status = _(u'Item moved up.')
            elif attempt > 1:
                self.status = _(u'Items moved up.')
            else:
                self.status = _(u'Nothing to change.')
        except ValueError:
            self.status = _(u'ValueError: Move failed.')
        return self._setRedirect('portal_types', 'object/new_contents')

    def handle_down(self, action, data):
        """Move the selected objects down the selected number of places"""
        ids = self._get_ids(data)
        delta = data.get('delta', 1)
        subset_ids = [obj.getId()
                       for obj in self.context.listFolderContents()]
        try:
            attempt = self.context.moveObjectsDown(ids, delta,
                                                 subset_ids=subset_ids)
            if attempt == 1:
                self.status = _(u'Item moved down.')
            elif attempt > 1:
                self.status = _(u'Items moved down.')
            else:
                self.status = _(u'Nothing to change.')
        except ValueError:
            self.status = _(u'ValueError: Move failed.')
        return self._setRedirect('portal_types', 'object/new_contents')
            
    def handle_top(self, action, data):
        """Move the selected objects to the top of the page"""
        ids = self._get_ids(data)
        subset_ids = [obj.getId()
                       for obj in self.context.listFolderContents()]
        try:
            attempt = self.context.moveObjectsToTop(ids,
                                                    subset_ids=subset_ids)
            if attempt == 1:
                self.status = _(u'Item moved to top.')
            elif attempt > 1:
                self.status = _(u'Items moved to top.')
            else:
                self.status = _(u'Nothing to change.')
        except ValueError:
            self.status = _(u'ValueError: Move failed.')
        return self._setRedirect('portal_types', 'object/new_contents')

    def handle_bottom(self, action, data):
        """Move the selected objects to the bottom of the page"""
        ids = self._get_ids(data)
        subset_ids = [obj.getId()
                       for obj in self.context.listFolderContents()]
        try:
            attempt = self.context.moveObjectsToBottom(ids,
                                                       subset_ids=subset_ids)
            if attempt == 1:
                self.status = _(u'Item moved to bottom.')
            elif attempt > 1:
                self.status = _(u'Items moved to bottom.')
            else:
                self.status = _(u'Nothing to change.')
        except ValueError:
            self.status = _(u'ValueError: Move failed.')
        return self._setRedirect('portal_types', 'object/new_contents')
        
    def handle_sort_order(self, action, data):
        """Set the sort options for the folder."""
        key = data['position']
        reverse = data.get('reverse', 0)
        self.context.setDefaultSorting(key, reverse)
        self.status = _(u"Sort order changed")
        return self._setRedirect('portal_types', 'object/new_contents')
        

class FolderView(BatchViewBase):

    """View for IFolderish.
    """

    @memoize
    def _get_items(self):
        (key, reverse) = self.context.getDefaultSorting()
        items = self.context.contentValues()
        items = sequence.sort(items,
                              ((key, 'cmp', reverse and 'desc' or 'asc'),))
        return LazyFilter(items, skip='View')

    @memoize
    def has_local(self):
        return 'local_pt' in self.context.objectIds()