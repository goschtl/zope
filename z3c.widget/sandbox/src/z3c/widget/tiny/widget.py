##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTML-Editor Widget using TinyMCE

$Id$
"""
__docformat__ = "reStructuredText"

try:
    from zc import resourcelibrary
    haveResourceLibrary = True
except ImportError:
    haveResourceLibrary = False
    
from zope.app.form.browser import TextAreaWidget
from zope.app.form.browser.widget import renderElement

template = """%(widget_html)s<script type="text/javascript">
tinyMCE.init({ 
mode : "exact",
language : "%(language)s",
theme : "%(theme)s",
%(optionals)s
elements : "%(name)s"}
);
</script>
"""

class TinyWidget(TextAreaWidget):


    """A WYSIWYG input widget for editing html which uses tinymce
    editor.

    >>> from zope.publisher.browser import TestRequest
    >>> from zope.schema import Text
    >>> field = Text(__name__='foo', title=u'on')
    >>> request = TestRequest(form={'field.foo': u'Hello\\r\\nworld!'})
    >>> widget = TinyWidget(field, request)
    >>> print widget()
    <textarea cols="60" id="field.foo" name="field.foo" rows="15" >Hello
    world!</textarea><script type="text/javascript">
    tinyMCE.init({ 
    mode : "exact",
    language : "en",
    theme : "advanced",
    elements : "field.foo"}
    );
    </script>

    """
    
    theme="advanced"
    valid_elements = None
    language="en"
    inline_styles=None
    valid_elements=None
    optionals = ['inline_styles','valid_elements']

    def __call__(self,*args,**kw):
        if haveResourceLibrary:
            resourcelibrary.need('tiny_mce')
        # elements == id
        # mode = exact
        optionals = []
        for k in self.optionals:
            v = getattr(self,k,None)
            v = v==True and 'true' or v==False and 'false' or v
            if v is not None:
                optionals.append('%s : "%s"' % (k,v))
        optionals = ','.join(optionals)
        widget_html =  super(TinyWidget,self).__call__(*args,**kw)
        return template % {"widget_html": widget_html,
                           "name": self.name,
                           "theme": self.theme,
                           "optionals": optionals,
                           "language": self.language}

