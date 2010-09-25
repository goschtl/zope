"""
Forms for managing members
"""
from logging import getLogger
LOG = getLogger("Manage Members Form")

from zope.interface import Interface
from zope.formlib import form
from zope.schema import Bool, TextLine, Date, getFieldsInOrder, List, Choice
from zope.sequencesort.ssort import sort

from ZTUtils import LazyFilter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.formlib.schema import EmailLine
from Products.CMFDefault.utils import Message as _

from Products.CMFDefault.browser.utils import memoize
from Products.CMFDefault.browser.content.folder import BatchViewBase
from Products.CMFDefault.browser.content.interfaces import IBatchForm

class IMemberItem(Interface):
    """Schema for portal members """

    select = Bool(
        required=False)

    name = TextLine(
        title=u"Name",
        required=False,
        readonly=True
        )
        
    email = TextLine(
        title=_(u"E-mail Address"),
        required=False,
        readonly=True
        )
        
    last_login = Date(
        title=_(u"Last Login"),
        required=False,
        readonly=True
        )


class MemberProxy(object):
    """Utility class wrapping a member for display purposes"""
    
    def __init__(self, member):
        login_time = member.getProperty('login_time')
        self.login_time = '2000/01/01' and '---' or login_time.Date()
        self.name = member.getId()
        self.home = member.getProperty('getHomeUrl')
        self.email = member.getProperty('email')
        self.widget = "%s.select" % self.name


class Manage(BatchViewBase, EditFormBase):
    
    label = _(u"Manage Members")
    template = ViewPageTemplateFile("members.pt")
    delete_template = ViewPageTemplateFile("members_delete.pt")
    guillotine = None
    form_fields = form.FormFields()
    hidden_fields = form.FormFields(IBatchForm)
    
    manage_actions = form.Actions(
        form.Action(
            name='new',
            label=_(u'New...'),
            success='handle_add',
            failure='handle_failure'),
        form.Action(
            name='select',
            label=_(u'Delete...'),
            condition='members_exist',
            success='handle_select_for_deletion',
            failure='handle_failure',
            validator=('validate_items')
                )
            )
            
    delete_actions = form.Actions(
        form.Action(
            name='delete',
            label=_(u'Delete'),
            success='handle_delete',
            failure='handle_failure'),
        form.Action(
            name='cancel',
            label=_(u'Cancel'),
            success='handle_cancel'
                )
            )
    actions = manage_actions + delete_actions

    def _get_items(self):
        mtool = self._getTool('portal_membership')
        return mtool.listMembers()
        
    def members_exist(self, action=None):
        return len(self._getBatchObj()) > 0

    def _get_ids(self, data):
        """Identify objects that have been selected"""
        ids = [k[:-7] for k, v in data.items()
                 if v is True and k.endswith('.select')]
        return ids
        
    def member_fields(self):
        """Create content field objects only for batched items
        Also create pseudo-widget for each item
        """
        f = IMemberItem['select']
        members = []
        fields = form.FormFields()
        for item in self._getBatchObj():
            field = form.FormField(f, 'select', item.getId())
            fields += form.FormFields(field)
            members.append(MemberProxy(item))
        self.listBatchItems = members
        return fields
        
    def setUpWidgets(self, ignore_request=False):
        """Create widgets for the members"""
        super(Manage, self).setUpWidgets(ignore_request)
        self.widgets = form.setUpWidgets(self.member_fields(), self.prefix,
                    self.context, self.request, ignore_request=ignore_request)

    def validate_items(self, action=None, data=None):
        """Check whether any items have been selected for
        the requested action."""
        super(Manage, self).validate(action, data)
        if self._get_ids(data) == []:
            return [_(u"Please select one or more items first.")]
        else:
            return []

    def handle_add(self, action, data):
        """Redirect to the join form where managers can add users"""
        return self._setRedirect('portal_actions', 'user/join')
        
    def handle_select_for_deletion(self, action, data):
        """Identify members to be deleted and redirect to confirmation
        template"""
        self.guillotine = ", ".join(self._get_ids(data))
        return self.delete_template()
        
    def handle_delete(self, action, data):
        """Delete selected members"""
        mtool = self._getTool('portal_membership')
        mtool.deleteMembers(self._get_ids(data))
        self.status = _(u"Selected members deleted")
        self._setRedirect('portal_actions', "global/manage_members")
        
    def handle_cancel(self, action, data):
        """Don't delete anyone, return to list"""
        self.status = _(u"Deletion broken off")
        self._setRedirect('portal_actions', "global/manage_members")


class Roster(BatchViewBase):
    
    hidden_fields = form.FormFields(IBatchForm)
    form_fields = form.FormFields()
    actions = ()
    template = ViewPageTemplateFile("members_list.pt")
    
    def mtool(self):
        return self._getTool('portal_membership')
    
    def isUserManager(self):
        return self.mtool().checkPermission('Manage users',
                          self.mtool().getMembersFolder()
                                            )
                                            
    @memoize
    def _get_items(self):
        (key, reverse) = self.context.getDefaultSorting()
        items = self.mtool().getRoster()
        items = sort(items, ((key, 'cmp', reverse and 'desc' or 'asc'),))
        return items
        return LazyFilter(items, skip='View')
                          
    def listBatchItems(self):
        members = []
        for item in self._getBatchObj():
            member = item
            member['home'] = self.mtool().getHomeUrl(item['id'],
                                verifyPermission=1)
            member['listed'] = member['listed'] and _(u"Yes") or _("No")
            members.append(member)
        return members
             