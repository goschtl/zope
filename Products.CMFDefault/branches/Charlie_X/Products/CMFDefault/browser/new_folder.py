from zope.interface import Interface
from zope.schema import Bool, TextLine
from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFDefault.browser.utils import ViewBase
from Products.CMFDefault.formlib.form import ContentEditFormBase
from Products.CMFDefault.utils import Message as _

class IFolderItem(Interface):
    """Interface for folderish objects contents."""
    
    select = Bool(
        required=False)
        
    name = TextLine(
        title=u"Name",
        required=False,
        readonly=True)

class ContentsView(ContentEditFormBase):
    """Folder contents view for camaoCmsMasterPages"""
    
    actions = form.Actions(
        form.Action(
            name='rename',
            label=_(u'Rename'),
            validator='check_items',
            success='handle_rename'),
        form.Action(
            name='cut',
            label=_(u'Cut'),
            validator='check_items',
            success='handle_cut'),
        form.Action(
            name='copy',
            label=_(u'Copy'),
            validator='check_items',
            success='handle_copy'),
        form.Action(
            name='paste',
            label=_(u'Paste'),
            condition='check_clipboard_data',
            success='handle_paste'),
        form.Action(
            name='delete',
            label=_(u'Delete'),
            validator='check_items',
            success='handle_delete'),
        form.Action(
            name='up',
            label=_(u'Up'),
            validator='check_items',
            success='handle_up'),
        form.Action(
            name='down',
            label=_(u'Down'),
            validator='check_items',
            success='handle_down'),
        form.Action(
            name='top',
            label=_(u'Top'),
            validator='check_items',
            success='handle_top'),
        form.Action(
            name='bottom',
            label=_(u'Bottom'),
            validator='check_items',
            success='handle_bottom')
            )
    
    template = ViewPageTemplateFile('templates/contents.pt')
    
    errors = ()
    
    
    def __init__(self, *args, **kw):
        super(ContentsView, self).__init__(*args, **kw)
        self.form_fields = form.FormFields()
        self.contents = self.context.contentValues()

        for item in self.contents:
            for n, f in schema.getFieldsInOrder(IFolderItem):
                field = form.FormField(f, n, item.id)
                self.form_fields += form.FormFields(field)
                
    def is_orderable(self):
        """Returns true if folder contents may be reordered"""
        pass
        
    def is_sortable(self):
        """Returns true if the folder contents view may be sorted for display"""
        pass
        
    def setUpWidgets(self, ignore_request=False):
        data = {}
        for i in self.contents:
            data['%s.name' %i.id] = i.id
        self.widgets = form.setUpDataWidgets(
                self.form_fields, self.prefix, self.context,
                self.request, data=data, ignore_request=ignore_request)
    
    def layout_fields(self):
        """Return the widgets for the form in the interface field order"""
        fields = []

        for index, item in enumerate(self.contents):
            field = {'ModificationDate':item.ModificationDate()}
            field['select'] = self.widgets['%s.select' % item.getId()]
            field['name'] = self.widgets['%s.name' % item.getId()]
            field['url'] = item.absolute_url()
            field['title'] = item.TitleOrId()
            field['icon'] = item.icon
            field['position'] = index + 1
            fields.append(field.copy())
        return fields
                
    def _get_ids(self, data):
        """Strip prefixes from ids that have been selected"""
        ids = [k.split(".")[0] for k, v in data.items() if v == True]
        return ids
        
    def check_items(self, action, data):
        """Check whether any items have been selected for the requested action."""
        errors = form.getWidgetsData(self.widgets, 'form', data)
        if len(self._get_ids(data)) == 0:
            return [_(u"Please select one or more items first.")]
        
    def check_clipboard_data(self, action):
        return bool(self.context.cb_dataValid())
    
    def handle_new(self, action, data):
        return self._setRedirect('portal_types', 'object/new')
    
    def handle_rename(self, action, data):
        ids = self._get_ids(data)
        new_ids = [str(data['%s.name' % k]) for k in ids]
        self.status = _(u'Item renamed.')
        self.context.manage_renameObjects(ids, new_ids)
        return self._setRedirect('portal_types', 'object/contents')
    
    def handle_cut(self, action, data):
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
        return self._setRedirect('portal_types', 'object/contents')    

    def handle_copy(self, action, data):
        ids = self._get_ids(data)

        try:
            self.context.manage_copyObjects(ids, self.request)
            if len(ids) == 1:
                self.status = _(u'Item copied.')
            else:
                self.status = _(u'Items copied.')
        except CopyError:
            self.status = _(u'CopyError: Copy failed.')
        return self._setRedirect('portal_types', 'object/contents')
    
    def handle_paste(self, action, data):
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
        return self._setRedirect('portal_types', 'object/contents')

    def handle_delete(self, action, data):
        ids = self._get_ids(data)
        self.context.manage_delObjects(list(ids))
        if len(ids) == 1:
            self.status = _(u'Item deleted.')
        else:
            self.status = _(u'Items deleted.')
        return self._setRedirect('portal_types', 'object/contents')
    
    def handle_up(self, action, data):
        ids = self._get_ids(data)
        delta = self.request.form.get('delta', 1)
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
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
        return self._setRedirect('portal_types', 'object/contents')

    def handle_down(self, action, data):
        ids = self._get_ids(data)
        delta = self.request.form.get('delta', 1)
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
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
        return self._setRedirect('portal_types', 'object/contents')
            
    def handle_top(self, action, data):
        ids = self._get_ids(data)
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
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
        return self._setRedirect('portal_types', 'object/contents')

    def handle_bottom(self, action, data):
        ids = self._get_ids(data)
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
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
        return self._setRedirect('portal_types', 'object/contents')
        
