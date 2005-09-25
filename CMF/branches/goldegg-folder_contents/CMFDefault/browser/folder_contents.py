from Products.Five.browser import BrowserView
from AccessControl import ClassSecurityInfo

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

from DocumentTemplate import sequence
    
class FolderContents(BrowserView):

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
        if not self.key:
            (self.key, self.reverse) = self.context.getDefaultSorting()
            return 1
        elif (self.key, self.reverse) == self.context.getDefaultSorting():
            return 1
        else:
            return 0

    def action(self):
        return self.context.getActionInfo(self._DEFAULT_TARGET)['url']

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        form = self.request.form
        default_target = self._DEFAULT_TARGET
        ids = form.get('ids', ())
        b_start = self.b_start = form.get('b_start', 0)
        key = self.key = form.get('key', '')
        reverse = self.reverse = form.get('reverse', '')
        default_kw = self.default_kw = {'b_start': b_start, 'key': key,
                                        'reverse': reverse}
        if 'items_copy' in form and \
                context.validateItemIds(**form) and \
                context.folder_copy_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif 'items_cut' in form and \
                context.validateItemIds(**form) and \
                context.folder_cut_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif 'items_delete' in form and \
                context.validateItemIds(**form) and \
                context.folder_delete_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif 'items_new' in form and \
                context.setRedirect(context, 'object/new'):
            return
        elif 'items_paste' in form and \
                context.folder_paste_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif 'items_rename' in form and \
                context.validateItemIds(**form) and \
                context.setRedirect(context, 'object/rename_items', ids=ids,
                                    **default_kw):
            return
        elif 'items_sort' in form and \
                context.folder_sort_control(**form) and \
                context.setRedirect(context, default_target, b_start=b_start):
            return
        elif 'items_up' in form and \
                context.validateItemIds(**form) and \
                context.folder_up_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif 'items_down' in form and \
                context.validateItemIds(**form) and \
                context.folder_down_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif 'items_top' in form and \
                context.validateItemIds(**form) and \
                context.folder_top_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        elif 'items_bottom' in form and \
                context.validateItemIds(**form) and \
                context.folder_bottom_control(**form) and \
                context.setRedirect(context, default_target, **default_kw):
            return
        return self.index()

    def up_info(self):
        if self._upitems_list_allowed():
            up_obj = self.context.aq_parent
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

    def batch(self):
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
            if self.key == column['key'] and not self.reverse and self.key != 'position':
                query = make_query(key=column['key'], reverse=1)
            else:
                query = make_query(key=column['key'])
            column['url'] = '%s?%s' % (self.action(), query)

        self.context.filterCookie()
        folderfilter = self.request.get('folderfilter', '')
        filter = self.context.decodeFolderFilter(folderfilter)
        items = self.context.listFolderContents(contentFilter=filter)
        items = sequence.sort( items, ((self.key, 'cmp', self.reverse and 'desc' or 'asc'),) )
        batch_obj = Batch(items, 25, self.b_start, orphan=0)
        items = self.items = []
        i = 1
        for item in batch_obj:
            item_icon = item.getIcon(1)
            item_id = item.getId()
            item_position = self.key == 'position' and str(self.b_start + i) or '...'
            i += 1
            item_url = item.getActionInfo( ('object/folderContents',
                                            'object/view') )['url']
            items.append( { 'checkbox': self._items_manage_allowed() and
                                        ('cb_%s' % item_id) or '',
                            'icon': item_icon and
                                    ( '%s/%s' % (self._portal_url(), item_icon) ) or '',
                            'id': item_id,
                            'modified': item.ModificationDate(),
                            'position': item_position,
                            'title': item.Title(),
                            'type': item.Type() or None,
                            'url': item_url } )
        navigation = self.context.getBatchNavigation(batch_obj, self.action(), **self.default_kw)
        self.length = batch_obj.sequence_length
        return { 'listColumnInfos': tuple(columns),
                 'listItemInfos': tuple(items),
                 'navigation': navigation }

    def form(self):
        hidden_vars = []
        for name, value in html_marshal(**self.default_kw):
            hidden_vars.append( {'name': name, 'value': value} )
        buttons = []
        if self._items_manage_allowed():
            if self._items_add_allowed() and self.context.allowedContentTypes():
                buttons.append( {'name': 'items_new', 'value': _('New...')} )
                if self.items:
                    buttons.append( {'name': 'items_rename', 'value': _('Rename')} )
            if self.items:
                buttons.append( {'name': 'items_cut', 'value': _('Cut')} )
                buttons.append( {'name': 'items_copy', 'value': _('Copy')} )
            if self._items_add_allowed() and self.context.cb_dataValid():
                buttons.append( {'name': 'items_paste', 'value': _('Paste')} )
            if self._items_delete_allowed() and self.items:
                buttons.append( {'name': 'items_delete', 'value': _('Delete')} )
        is_orderable = self._items_move_allowed() and (self.key == 'position') and self.length > 1
        is_sortable = self._items_move_allowed() and not self._is_default()
        deltas = range( 1, min(5, self.length) ) + range(5, self.length, 5)
        return { 'listHiddenVarInfos': tuple(hidden_vars),
                 'listButtonInfos': tuple(buttons),
                 'listDeltas': tuple(deltas),
                 'is_orderable': is_orderable,
                 'is_sortable': is_sortable }
