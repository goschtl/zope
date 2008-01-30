from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest,IBrowserSkinType
from zope.component import getGlobalSiteManager
from zope.publisher.interfaces import IRequest
import zope.interface
import urllib

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.security.proxy import removeSecurityProxy
from zope.interface import providedBy
from zope.session.interfaces import ISession
from zope.app import zapi

from z3c.securitytool.securitytool import settingsForObject
from z3c.securitytool.interfaces import ISecurityChecker

SESSION_KEY = 'securitytool'
                                                    
class ViewPrincipalMatrix(BrowserView):
    """ This is the view used to populate the vum.html
        (securitytool main page)
    """
    
    pageTemplateFile = "viewprincipalmatrix.pt"
    
    evenOddClasses = ('even','odd')
    evenodd = 0
    
    def update(self):
        self.viewList = {}
        selectedPermission = None
        if 'FILTER' in self.request.form:
            selectedSkin = self.request.form['selectedSkin']
            ISession(self.request)[SESSION_KEY]['selectedSkin'] = selectedSkin
            skin = zapi.getUtility(IBrowserSkinType,selectedSkin)
            if (self.request.form.has_key('selectedPermission') and
                self.request.form['selectedPermission'] != 'None'):
                selectedPermission = self.request.form['selectedPermission']
        else:
            skin = IBrowserRequest
        
        ifaces = tuple(providedBy(self.context))
        security_checker = ISecurityChecker(self.context)

        self.viewMatrix, self.views, self.permissions = \
            security_checker.getPermissionSettingsForAllViews(ifaces, skin,
            selectedPermission)


        # self.views is a dict in the form of {view:perm}
        # Here It would make more sense to group by permission rather than view
        sortedViews = sorted([(v,k) for k,v in self.views.items()])

        for item in sortedViews:
            if self.viewList.has_key(item[0]):
                self.viewList[item[0]].append(item[1])
            else:
                self.viewList[item[0]] = [item[1]]
                            
        
    def cssclass(self):
        """ determiner what background color to use for lists """
        if self.evenodd != 1:
            self.evenodd = 1
        else:
            self.evenodd = 0
        return self.evenOddClasses[self.evenodd]
        
    
    def getPermissionSetting(self, view, principal):
        try:
            return self.viewMatrix[principal][view]
        except KeyError:
            return '--'

    @property
    def skinTypes(self):   
        """ gets all the available skins on the system """
        skinNames = {}
        for name, util in zapi.getUtilitiesFor(IBrowserSkinType, self.context):
            skinNames[name] = False
            if (self.request.form.has_key('selectedSkin') and
                self.request.form['selectedSkin'] == name):
                skinNames[name] = True
        return skinNames
    
    @property
    def urlEncodedViewName(self):
        """ properly formats variables for use in urls """
        urlNames = {}
        for key in self.views.keys():
            urlNames[key] = urllib.quote(key)
        return urlNames
        

    def getPermissionList(self):
        """ returns sorted permission list"""
        return sorted(self.permissions)

    def render(self):
        return  ViewPageTemplateFile(self.pageTemplateFile)(self)

    def __call__(self):
        self.update()
        return self.render()

class PrincipalDetails(BrowserView):
    """ view class for ud.html (User Details)"""
    pageTemplateFile = "principalinfo.pt"

    def update(self):
        if self.request.form.has_key('principal'):
            self.principal = self.request.form['principal']
        else:
            self.principal = 'no principal specified'

        skin = getSkin(self.request) or IBrowserRequest

        self.legend = (u"<span class='Deny'>Red Bold = Denied Permission"
                       u"</span>,<span class='Allow'> Green Normal = "
                       u"Allowed Permission </span>")

        principal_security = ISecurityChecker(self.context)
        self.principalPermissions = principal_security.principalPermissions(
            self.principal, skin=skin)

        self.legend = (u"<span class='Deny'>Red Bold = Denied Permission"
                       u"</span>,<span class='Allow'> Green Normal = "
                       u"Allowed Permission </span>")

    def render(self):
        return ViewPageTemplateFile(self.pageTemplateFile)(self)

    def __call__(self):
        self.update()
        return self.render()

class PermissionDetails(BrowserView):
    """ view class for pd.html (Permission Details)"""
    
    pageTemplateFile = "permdetails.pt"

    def update(self):
        if self.request.form.has_key('principal'):
            self.principal = self.request.form['principal']
        else:
            self.principal = 'no user specified'

        if self.request.form.has_key('view'):
            self.view = self.request.form['view']
        else:
            self.view = 'no view specified'

        skin = getSkin(self.request) or IBrowserRequest
        
        principal_security = ISecurityChecker(self.context)

        self.permissionDetails = principal_security.permissionDetails(
            self.principal, self.view, skin=skin)

        self.read_perm = self.permissionDetails['read_perm']
        if self.read_perm == 'zope.Public':
            self.message =(u"<p class=\"Allow\"> The view <b>%s</b> has the permission "
                           u"<b>zope.Public</b> and can  be accessed "
                           u"by any principal.</p>" % self.view)

            self.legend = u""
        else:
            self.message = (u"These are the security settings for the "
                            u"principal <b>%(principal)s</b> and the view "
                            u"<b>%(view)s</b> with the permission "
                            u"<b>%(read_perm)s</b>."
                            % self.__dict__
                             )
                          
            self.legend = (u"<span class='Deny'>Red Bold = Denied Permission"
                           u"</span>,<span class='Allow'> Green Normal = "
                           u"Allowed Permission </span>")

    def render(self):
        return ViewPageTemplateFile(self.pageTemplateFile)(self)

    def __call__(self):
        self.update()
        return self.render()

def getSkin(request):
    """Get the skin from the session."""
    sessionData = ISession(request)[SESSION_KEY]
    selectedSkin = sessionData.get('selectedSkin', IBrowserRequest)
    return zapi.queryUtility(IBrowserSkinType, selectedSkin)
