from zope.app.form.browser.widget import DisplayWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.form.browser import TextAreaWidget
import hurry.tinymce

template = """%(widget_html)s<script type="text/javascript">
tinyMCE.init({
mode : "exact", %(options)s
elements : "%(name)s"
}
);
</script>
"""

OPT_PREFIX="mce_"
OPT_PREFIX_LEN = len(OPT_PREFIX)
MCE_LANGS=[]
import glob
import os

# initialize the language files
for langFile in glob.glob(
    os.path.join(os.path.dirname(hurry.tinymce.__file__),'tinymce-build','langs') + '/??.js'):
    MCE_LANGS.append(os.path.basename(langFile)[:2])


class TinyWidget(TextAreaWidget):


    """A WYSIWYG input widget for editing html which uses tinymce
    editor.

    First we need to grok `hurry.zoperesource`

    >>> from grok.testing import grok
    >>> grok('hurry.zoperesource')

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Text
    >>> field = Text(__name__='foo', title=u'on')
    >>> request = TestRequest(
    ...     form={'field.foo': u'Hello\\r\\nworld!'})

    By default, only the needed options to MCE are passed to
    the init method.

    >>> widget = TinyWidget(field, request)
    >>> print widget()
    <textarea cols="60" id="field.foo" name="field.foo" rows="15" >Hello
    world!</textarea><script type="text/javascript">
    tinyMCE.init({
    mode : "exact",
    elements : "field.foo"
    }
    );
    </script>

    All variables defined on the object which start with ``mce_`` are
    passed to the init method. Python booleans are converted
    automatically to their js counterparts.

    For a complete list of options see:
    http://tinymce.moxiecode.com/tinymce/docs/reference_configuration.html

    >>> widget = TinyWidget(field, request)
    >>> widget.mce_theme="advanced"
    >>> widget.mce_ask=True
    >>> print widget()
    <textarea ...
    tinyMCE.init({
    mode : "exact", ask : true, theme : "advanced",
    elements : "field.foo"
    }
    );
    </script>

    Also the string literals "true" and "false" are converted to js
    booleans. This is usefull for widgets created by zcml.

    >>> widget = TinyWidget(field, request)
    >>> widget.mce_ask='true'
    >>> print widget()
    <textarea ...
    mode : "exact", ask : true,
    ...
    </script>

    Languages are taken from the tinymce-build/langs directory in
    hurry.tinymce (currently only English language it's available).

    >>> print MCE_LANGS
    ['en']

    If the language is found it is added to the mce options. To test
    this behaviour we simply set the language directly, even though it
    is a readonly attribute (don't try this at home)

    >>> request.locale.id.language='en'
    >>> print widget()
    <textarea ...
    mode : "exact", ask : true, language : "en",
    ...
    </script>

    """

    def __call__(self,*args,**kw):
        hurry.tinymce.tinymce.need()

        mceOptions = []
        for k in dir(self):
            if k.startswith(OPT_PREFIX):
                v = getattr(self,k,None)
                v = v==True and 'true' or v==False and 'false' or v
                if v in ['true','false']:
                    mceOptions.append('%s : %s' % (k[OPT_PREFIX_LEN:],v))
                elif v is not None:
                    mceOptions.append('%s : "%s"' % (k[OPT_PREFIX_LEN:],v))
        mceOptions = ', '.join(mceOptions)
        if mceOptions:
            mceOptions += ', '
        if self.request.locale.id.language in MCE_LANGS:
            mceOptions += ('language : "%s", ' % \
                           self.request.locale.id.language)
        widget_html =  super(TinyWidget,self).__call__(*args,**kw)
        return template % {"widget_html": widget_html,
                           "name": self.name,
                           "options": mceOptions}



class TinyDisplayWidget(DisplayWidget):
    template = ViewPageTemplateFile('tinydisplaywidget.pt')

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = ""
        return self.template(name=self.context.__name__, value=value)