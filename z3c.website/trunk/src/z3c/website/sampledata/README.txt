======================
Sample Data Generation
======================

Setup the test browser and go to the sampledata.html page.

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False


Setup z3c.website
-----------------

  >>> browser.open('http://localhost/@@managesamples.html')
  >>> browser.getLink(text='z3c.website').click()
  >>> browser.url
  'http://localhost/@@generatesample.html?manager=z3c.website'

Now we fill in the form and generate the sample site.

  >>> browser.getControl(name='generator.seed').value = 'sample'
  >>> browser.getControl(name='z3c.website.site.__name__').value = 'z3c'
  >>> browser.getControl(name='z3c.website.site.title').value = 'Z3C'
  >>> browser.getControl('Generate').click()

Let's access the new z3c website within the skin:

  >>> browser.open('http://localhost/++skin++Z3CWebSite/z3c')
  >>> browser.url
  'http://localhost/++skin++Z3CWebSite/z3c'

Thre is also content:

  >>> browser.open('http://localhost/++skin++Z3CWebSite/z3c/contact/index.html')
  >>> browser.url
  'http://localhost/++skin++Z3CWebSite/z3c/contact/index.html'

  >>> print browser.contents
  <!DOCTYPE ...
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
        lang="en">
  <head>
  <title>z3c.org: Contact</title><meta http-equiv="cache-control" content="no-cache" />
  <meta http-equiv="pragma" content="no-cache" />
  <script type="text/javascript">
    var contextURL='http://localhost/++skin++Z3CWebSite/z3c/contact/';
    var viewURL='http://localhost/++skin++Z3CWebSite/z3c/contact/index.html/'</script>
  <script type="text/javascript"
          src="http://localhost/++skin++Z3CWebSite/z3c/@@/xmlhttp.js">
  </script>
  <BLANKLINE>
  <script type="text/javascript"
          src="http://localhost/++skin++Z3CWebSite/z3c/@@/json.js">
  </script>
  <BLANKLINE>
  <script type="text/javascript"
          src="http://localhost/++skin++Z3CWebSite/z3c/@@/jquery.pack.js">
  </script>
  <BLANKLINE>
  <script type="text/javascript"
          src="http://localhost/++skin++Z3CWebSite/z3c/@@/jsonform.validate.js">
  </script>
  <BLANKLINE>
  <script type="text/javascript"
          src="http://localhost/++skin++Z3CWebSite/z3c/@@/interface.js">
  </script>
  <BLANKLINE>
  <script type="text/javascript"
          src="http://localhost/++skin++Z3CWebSite/z3c/@@/jquery.resteditor.js">
  </script>
  <BLANKLINE>
  <script type="text/javascript"
          src="http://localhost/++skin++Z3CWebSite/z3c/@@/demo.js">
  </script>
  <BLANKLINE>
  <link type="text/css" rel="stylesheet"
        href="http://localhost/++skin++Z3CWebSite/z3c/@@/div-form.css"
        media="all" />
  <BLANKLINE>
  <link type="text/css" rel="stylesheet"
        href="http://localhost/++skin++Z3CWebSite/z3c/@@/jsonform.validate.css"
        media="all" />
  <BLANKLINE>
  <link type="text/css" rel="stylesheet"
        href="http://localhost/++skin++Z3CWebSite/z3c/@@/demo.css"
        media="all" />
  <BLANKLINE>
  <link type="text/css" rel="stylesheet"
        href="http://localhost/++skin++Z3CWebSite/z3c/@@/resteditor.css"
        media="all" />
  <BLANKLINE>
  <link rel="icon" type="image/png"
        href="http://localhost/++skin++Z3CWebSite/z3c/@@/favicon.png" />
  </head>
  <body>
  ...
  </body>
  </html>
