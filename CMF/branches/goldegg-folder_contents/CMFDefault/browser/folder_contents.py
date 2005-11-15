from DocumentTemplate import sequence
from ZTUtils import Batch
from ZTUtils import make_query

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import AddPortalContent
from Products.CMFDefault.permissions import DeleteObjects
from Products.CMFDefault.permissions import ListFolderContents
from Products.CMFDefault.permissions import ManageProperties
from Products.CMFDefault.permissions import ViewManagementScreens
from Products.CMFDefault.utils import html_marshal
from Products.CMFDefault.utils import MessageID as _


class FolderContents:

    """Folder contents view.
    """

    _DEFAULT_TARGET = 'object/folderContents'

    def _portal_url(self):
        utool = getToolByName(self.context, 'portal_url')
        return utool()

    def _upitems_list_allowed(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission(ListFolderContents, self.context,
                                     'aq_parent')

    def _items_manage_allowed(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission(ViewManagementScreens, self.context)

    def _items_delete_allowed(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission(DeleteObjects, self.context)

    def _items_add_allowed(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission(AddPortalContent, self.context)

    def _items_move_allowed(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission(ManageProperties, self.context)

    def _is_default(self):
        if (self._key, self._reverse) == self.context.getDefaultSorting():
            return True
        else:
            return False

    def __call__(self, b_start=0, key='', reverse=0, ids=(), delta=1,
                 items_copy='', items_cut='', items_delete='', items_new='',
                 items_paste='', items_rename='', items_up='', items_down='',
                 items_top='', items_bottom='', items_sort=''):
        context = self.context
        form = self.request.form
        default_target = self._DEFAULT_TARGET
        default_kw = {'b_start': b_start, 'key': key, 'reverse': reverse}
        if items_copy and \
                context.validateItemIds(**form) and \
                context.folder_copy_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif items_cut and \
                context.validateItemIds(**form) and \
                context.folder_cut_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif items_delete and \
                context.validateItemIds(**form) and \
                context.folder_delete_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif items_new and \
                context.setRedirect(context, 'object/new'):
            return
        elif items_paste and \
                context.folder_paste_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif items_rename and \
                context.validateItemIds(**form) and \
                context.setRedirect(context, 'object/rename_items', ids=ids,
                                    **default_kw):
            return
        elif items_sort and \
                context.folder_sort_control(**form) and \
                context.setRedirect(context, default_target, b_start=b_start):
            return
        elif items_up and \
                context.validateItemIds(**form) and \
                context.folder_up_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif items_down and \
                context.validateItemIds(**form) and \
                context.folder_down_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif items_top and \
                context.validateItemIds(**form) and \
                context.folder_top_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif items_bottom and \
                context.validateItemIds(**form) and \
                context.folder_bottom_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return

        if not key:
            (key, reverse) = self.context.getDefaultSorting()
        self.context.filterCookie()
        folderfilter = self.request.get('folderfilter', '')
        filter = self.context.decodeFolderFilter(folderfilter)
        items = self.context.listFolderContents(contentFilter=filter)
        items = sequence.sort(items,
                              ((key, 'cmp', reverse and 'desc' or 'asc'),))
        batch_obj = Batch(items, 25, b_start, orphan=0)

        self._batch_obj = batch_obj
        self._length = batch_obj.sequence_length
        self._b_start = b_start
        self._default_kw = default_kw
        self._key = key
        self._reverse = reverse
        return self.index()

    def action(self):
        return self.context.getActionInfo(self._DEFAULT_TARGET)['url']

    def up_info(self):
        if self._upitems_list_allowed():
            up_obj = self.context.aq_inner.aq_parent
            if hasattr(up_obj, 'portal_url'):
                up_url = up_obj.getActionInfo('object/folderContents')['url']
                return {'icon': '%s/UpFolder_icon.gif' % self._portal_url(),
                        'id': up_obj.getId(),
                        'url': up_url }
            else:
                return {'icon': '',
                        'id': 'Root',
                        'url': ''}
        else:
            return {}

    def listColumnInfos(self):
        columns = ( {'key': 'Type',
                     'title': _('Type'),
                     'width': '20',
                     'colspan': '2'}
                  , {'key': 'getId',
                     'title': _('Name'),
                     'width': '360',
                     'colspan': None}
                  , {'key': 'modified',
                     'title': _('Last Modified'),
                     'width': '180',
                     'colspan': None}
                  , {'key': 'position',
                     'title': _('Position'),
                     'width': '80',
                     'colspan': None }
                  )
        for column in columns:
            if self._key == column['key'] and not self._reverse and \
                    self._key != 'position':
                query = make_query(key=column['key'], reverse=1)
            else:
                query = make_query(key=column['key'])
            column['url'] = '%s?%s' % (self.action(), query)
        return tuple(columns)

    def listItemInfos(self):
        items = []
        i = 1
        for item in self._batch_obj:
            item_icon = item.getIcon(1)
            item_id = item.getId()
            item_position = self._key == 'position' and \
                            str(self._b_start + i) or '...'
            i += 1
            item_url = item.getActionInfo(('object/folderContents',
                                           'object/view'))['url']
            items.append({'checkbox': self._items_manage_allowed() and
                                      ('cb_%s' % item_id) or '',
                          'icon': item_icon and ('%s/%s' %
                                       (self._portal_url(), item_icon)) or '',
                          'id': item_id,
                          'modified': item.ModificationDate(),
                          'position': item_position,
                          'title': item.Title(),
                          'type': item.Type() or None,
                          'url': item_url})
        return tuple(items)

    def navigation(self):
        return self.context.getBatchNavigation(self._batch_obj, self.action(),
                                               **self._default_kw)

    def listHiddenVarInfos(self):
        hidden_vars = []
        for name, value in html_marshal(**self._default_kw):
            hidden_vars.append( {'name': name, 'value': value} )
        return tuple(hidden_vars)

    def listButtonInfos(self):
        buttons = []
        if self._items_manage_allowed():
            if self._items_add_allowed() and \
                    self.context.allowedContentTypes():
                buttons.append({'name': 'items_new', 'value': _('New...')})
                if self._length:
                    buttons.append({'name': 'items_rename',
                                    'value': _('Rename')})
            if self._length:
                buttons.append({'name': 'items_cut', 'value': _('Cut')})
                buttons.append({'name': 'items_copy', 'value': _('Copy')})
            if self._items_add_allowed() and self.context.cb_dataValid():
                buttons.append({'name': 'items_paste', 'value': _('Paste')})
            if self._items_delete_allowed() and self._length:
                buttons.append({'name': 'items_delete', 'value': _('Delete')})
        return tuple(buttons)

    def listDeltas(self):
        deltas = range(1, min(5, self._length)) + range(5, self._length, 5)
        return tuple(deltas)

    def is_orderable(self):
        return self._items_move_allowed() and (self._key == 'position') and \
                self._length > 1

    def is_sortable(self):
        return self._items_move_allowed() and not self._is_default()

    def batch(self):
        return {'listColumnInfos': self.listColumnInfos(),
                'listItemInfos': self.listItemInfos(),
                'navigation': self.navigation()}

    def form(self):
        return {'listHiddenVarInfos': self.listHiddenVarInfos(),
                'listButtonInfos': self.listButtonInfos(),
                'listDeltas': self.listDeltas(),
                'is_orderable': self.is_orderable(),
                'is_sortable': self.is_sortable()}
