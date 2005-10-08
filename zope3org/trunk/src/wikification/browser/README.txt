For our Wiki we use a PageInfo object. Its like a renderable PageTemplate
namespace. 

>>> from zope.pagetemplate.pagetemplate import PageTemplate
>>> from wikification.browser.utils import PageInfo
>>> template = PageTemplate()
>>> template.pt_edit(u'<span tal:replace="foo"/>', 'text/html')
>>> context = 'context' 
>>> request = TestRequest()
>>> page = PageInfo(context, request, template)
>>> page.foo = 'bar'
>>> page.render()
u'bar\n'

A WikiPageInfo is a specialized PageInfo. We also use a SiteInfo
object for site specific informations.

>>> from wikification.browser.utils import SiteInfo 
>>> from wikification.browser.utils import WikiPageInfo
>>> site = SiteInfo(context)
>>> page = WikiPageInfo(u'Wiki page', site, context, request, template)
>>> page.html_title()
u'Wiki page - Wiki site'

We can override the title later

>>> page.title = u'Custom title'
>>> page.html_title()
u'Custom title - Wiki site'

The html_title and title are available in the page template namespace now.

>>> template.pt_edit(u'<title tal:content="html_title"/>', 'text/html')
>>> page.render()
u'<title>Custom title - Wiki site</title>\n'
>>> template.pt_edit(u'<h1 tal:content="title"/>', 'text/html')
>>> page.render()
u'<h1>Custom title</h1>\n'

Our PageInfo object also has a macro mapping. So we can easily map macros to names.

>>> macro_template = PageTemplate()
>>> macro_template.pt_edit(u'<div metal:define-macro="foo">bar</div>', 'text/html')
>>> page.macros.update(macro_template.macros)
>>> template.pt_edit(u'<div metal:use-macro="macros/foo"/>', 'text/html')
>>> page.render()
u'<div>bar</div>\n'
