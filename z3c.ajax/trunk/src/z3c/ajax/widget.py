from zope.app.form.browser.textwidgets import TextWidget as BaseTextWidget
from interfaces import IAjaxWidget
from zope import interface, component
from zope.publisher.browser import BrowserPage
from xml.sax.saxutils import quoteattr, escape
from zope.app.form.browser.textwidgets import renderElement
from zc import resourcelibrary
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.form.interfaces import WidgetInputError

class BaseAjaxWidget(BaseTextWidget):
    interface.implements(IAjaxWidget)
    containerTag='span'

    def __init__(self,*args,**kw):
        resourcelibrary.need('z3c_ajax')
        super(BaseTextWidget,self).__init__(*args,**kw)
        if self.request:
            self.request.response.setHeader('Content-Type','text/html')

    def getValue(self):
        return self.context.get(self.context.context)

    def getURL(self):

        """returns the name of the form"""
        #TODO make an absolute_url view for this
        #import pdb;pdb.set_trace()
        
        url =absoluteURL(self.__form__,self.request)
        
        formName = url.split('/')[-1]
        contextURL = absoluteURL(self.__form__.context,self.request)
        return '%s/++ajax++%s/%s' % (contextURL,self.__form__.__name__,
                                     self.name)

    def __call__(self):
        resourcelibrary.need('z3c_ajax')
        html =  renderElement(self.containerTag,
                              cssClass='ajax:container',
                              extra='ajax:src="%s/display"' % self.getURL(),
                              contents='Loading ...')
        return html

    def renderInput(self):
        self.applyMethods()

    def renderDisplay(self):
        self.applyMethods()
        
    def applyMethods(self):
        pass
        

class TextWidget(BaseAjaxWidget):

    inputOnBlur = "z3cChangeView(this,'display?apply=1&' + this.name +'='+$F(this))"
    displayOnClick = "z3cChangeView(this,'input')"
    
    def applyMethods(self):
        if 'apply' in self.request.form:
            try:
                self.applyChanges(self.context.context)
            except WidgetInputError,e:
                # XXX to some valueable default here
                pass


    def renderInput(self):
        self.applyMethods()
        resourcelibrary.need('z3c_ajax')
        value = self.getValue()
        self.setRenderedValue(value)
        value = self._getFormValue()
        if value is None or value == self.context.missing_value:
            value = ''

        kwargs = {'type': self.type,
                  'name': self.name,
                  'id': self.name,
                  'value': value,
                  'cssClass': self.cssClass,
                  'style': self.style,
                  'onblur':self.inputOnBlur,
                  'size': self.displayWidth,
                  'extra': self.extra}
        if self.displayMaxWidth:
            kwargs['maxlength'] = self.displayMaxWidth

        contents = renderElement(self.tag, **kwargs)
        return contents

    def renderDisplay(self):
        self.applyMethods()
        resourcelibrary.need('z3c_ajax')
        value = self.getValue()
        contents = renderElement(self.containerTag,
                                 name=self.name,
                                 id=self.name,
                                 contents=value,
                                 onclick=self.displayOnClick)
        return contents


from zope.formlib import form

from zope.app.container.contained import ContainedProxy
from zope.security.proxy import removeSecurityProxy

class ListWidget(BaseAjaxWidget):

    # factory has to take a unicode as constructor
    contentFactory = None
    subFormName = u'edit.html'
    containerTag='div'
    added = None
    deleted = None
    
    def items(self):

        """returns (idx,value) of original value in order to keep the
        appopriate indexes intact"""
        
        value = self.getValue()
        return zip(range(len(value)),value)


    def applyMethods(self):
        if not hasattr(self,'value'):
            raise RuntimeError,u"self.value is not set"
        if 'add' in self.request.form and self.added is None:
            self.createAndAdd(self.request.form.get('add'))
        if 'delete' in self.request.form and self.deleted is None:
            value = self.getValue()
            idx = int(self.request.form.get('delete'))
            del value[idx]
            self.deleted = idx


    def renderDisplay(self):
        self.applyMethods()
        resourcelibrary.need('z3c_ajax')
        value = self.getValue()
        html = u''
        index=0
        #import pdb;pdb.set_trace()
        for item in value:
            item = ContainedProxy(removeSecurityProxy(item))
            item.__parent__=value
            item.__name__=unicode(index)
            sf =component.getMultiAdapter((item, self.request),
                                          name=self.subFormName)
            #sf = self._subForm(item,self.request)
            sf.setPrefix('%s.%s' % (self.name,index))
            sf.update()
            for widget in sf.widgets:
                widget.__form__=sf
            print "url------",
            html += u'<div>%s</div>' % sf.widgets['title']()
            index+=1
        onClick = """z3cChangeView(this,'display?add=1')"""
        html += '<div onclick="%s">+</div>' % onClick
        return html

    def createAndAdd(self,*args):
        value = self.getValue()
        o = self.contentFactory(*args)
        self.added=o
        value.append(o)


from zope.security.proxy import removeSecurityProxy
class Page(object):

    def __call__(self):
        return removeSecurityProxy(self.context)()

    def display(self):
        return removeSecurityProxy(self.context).renderDisplay()

    def input(self):
        return removeSecurityProxy(self.context).renderInput()
