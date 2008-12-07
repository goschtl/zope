   [1]SourceForge.net Logo

                                   mechanize

   Stateful programmatic web browsing in Python, after Andy Lester's Perl
   module [2]WWW::Mechanize .
     * mechanize.Browser is a subclass of mechanize.UserAgentBase, which
       is, in turn, a subclass of urllib2.OpenerDirector (in fact, of
       mechanize.OpenerDirector), so:
          + any URL can be opened, not just http:
          + mechanize.UserAgentBase offers easy dynamic configuration of
            user-agent features like protocol, cookie, redirection and
            robots.txt handling, without having to make a new
            OpenerDirector each time, e.g. by calling build_opener().
     * Easy HTML form filling, using [3]ClientForm interface.
     * Convenient link parsing and following.
     * Browser history (.back() and .reload() methods).
     * The Referer HTTP header is added properly (optional).
     * Automatic observance of [4]robots.txt.
     * Automatic handling of HTTP-Equiv and Refresh.

Examples

   This documentation is in need of reorganisation and extension!

   The two below are just to give the gist. There are also some [5]actual
   working examples.
import re
from mechanize import Browser

br = Browser()
br.open("http://www.example.com/")
# follow second link with element text matching regular expression
response1 = br.follow_link(text_regex=r"cheese\s*shop", nr=1)
assert br.viewing_html()
print br.title()
print response1.geturl()
print response1.info()  # headers
print response1.read()  # body
response1.close()  # (shown for clarity; in fact Browser does this for you)

br.select_form(name="order")
# Browser passes through unknown attributes (including methods)
# to the selected HTMLForm (from ClientForm).
br["cheeses"] = ["mozzarella", "caerphilly"]  # (the method here is __setitem__)
response2 = br.submit()  # submit current form

# print currently selected form (don't call .submit() on this, use br.submit())
print br.form

response3 = br.back()  # back to cheese shop (same data as response1)
# the history mechanism returns cached response objects
# we can still use the response, even though we closed it:
response3.seek(0)
response3.read()
response4 = br.reload()  # fetches from server

for form in br.forms():
    print form
# .links() optionally accepts the keyword args of .follow_/.find_link()
for link in br.links(url_regex="python.org"):
    print link
    br.follow_link(link)  # takes EITHER Link instance OR keyword args
    br.back()

   You may control the browser's policy by using the methods of
   mechanize.Browser's base class, mechanize.UserAgent. For example:
br = Browser()
# Explicitly configure proxies (Browser will attempt to set good defaults).
# Note the userinfo ("joe:password@") and port number (":3128") are optional.
br.set_proxies({"http": "joe:password@myproxy.example.com:3128",
                "ftp": "proxy.example.com",
                })
# Add HTTP Basic/Digest auth username and password for HTTP proxy access.
# (equivalent to using "joe:password@..." form above)
br.add_proxy_password("joe", "password")
# Add HTTP Basic/Digest auth username and password for website access.
br.add_password("http://example.com/protected/", "joe", "password")
# Don't handle HTTP-EQUIV headers (HTTP headers embedded in HTML).
br.set_handle_equiv(False)
# Ignore robots.txt.  Do not do this without thought and consideration.
br.set_handle_robots(False)
# Don't add Referer (sic) header
br.set_handle_referer(False)
# Don't handle Refresh redirections
br.set_handle_refresh(False)
# Don't handle cookies
br.set_cookiejar()
# Supply your own mechanize.CookieJar (NOTE: cookie handling is ON by
# default: no need to do this unless you have some reason to use a
# particular cookiejar)
br.set_cookiejar(cj)
# Log information about HTTP redirects and Refreshes.
br.set_debug_redirects(True)
# Log HTTP response bodies (ie. the HTML, most of the time).
br.set_debug_responses(True)
# Print HTTP headers.
br.set_debug_http(True)

# To make sure you're seeing all debug output:
logger = logging.getLogger("mechanize")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

# Sometimes it's useful to process bad headers or bad HTML:
response = br.response()  # this is a copy of response
headers = response.info()  # currently, this is a mimetools.Message
headers["Content-type"] = "text/html; charset=utf-8"
response.set_data(response.get_data().replace("<!---", "<!--"))
br.set_response(response)

   mechanize exports the complete interface of urllib2:
import mechanize
response = mechanize.urlopen("http://www.example.com/")
print response.read()

   so anything you would normally import from urllib2 can (and should, by
   preference, to insulate you from future changes) be imported from
   mechanize instead. In many cases if you import an object from mechanize
   it will be the very same object you would get if you imported from
   urllib2. In many other cases, though, the implementation comes from
   mechanize, either because bug fixes have been applied or the
   functionality of urllib2 has been extended in some way.

UserAgent vs UserAgentBase

   mechanize.UserAgent is a trivial subclass of mechanize.UserAgentBase,
   adding just one method, .set_seekable_responses() (see the
   [6]documentation on seekable responses).

   The reason for the extra class is that mechanize.Browser depends on
   seekable response objects (because response objects are used to
   implement the browser history).

Compatibility

   These notes explain the relationship between mechanize, ClientCookie,
   cookielib and urllib2, and which to use when. If you're just using
   mechanize, and not any of those other libraries, you can ignore this
   section.
    1. mechanize works with Python 2.4, Python 2.5, and Python 2.6.
    2. ClientCookie is no longer maintained as a separate package. The
       code is now part of mechanize, and its interface is now exported
       through module mechanize (since mechanize 0.1.0). Old code can
       simply be changed to import mechanize as ClientCookie and should
       continue to work.
    3. The cookie handling parts of mechanize are in Python 2.4 standard
       library as module cookielib and extensions to module urllib2.

   IMPORTANT: The following are the ONLY cases where mechanize and urllib2
   code are intended to work together. For all other code, use mechanize
   exclusively: do NOT mix use of mechanize and urllib2!
    1. Handler classes that are missing from 2.4's urllib2 (e.g.
       HTTPRefreshProcessor, HTTPEquivProcessor, HTTPRobotRulesProcessor)
       may be used with the urllib2 of Python 2.4 or newer. There are not
       currently any functional tests for this in mechanize, however, so
       this feature may be broken.
    2. If you want to use mechanize.RefreshProcessor with Python >= 2.4's
       urllib2, you must also use mechanize.HTTPRedirectHandler.
    3. mechanize.HTTPRefererProcessor requires special support from
       mechanize.Browser, so cannot be used with vanilla urllib2.
    4. mechanize.HTTPRequestUpgradeProcessor and
       mechanize.ResponseUpgradeProcessor are not useful outside of
       mechanize.
    5. Request and response objects from code based on urllib2 work with
       mechanize, and vice-versa.
    6. The classes and functions exported by mechanize in its public
       interface that come straight from urllib2 (e.g. FTPHandler, at the
       time of writing) do work with mechanize (duh ;-). Exactly which of
       these classes and functions come straight from urllib2 without
       extension or modification will change over time, though, so don't
       rely on it; instead, just import everything you need from
       mechanize, never from urllib2. The exception is usage as described
       in the first item in this list, which is explicitly OK (though not
       well tested ATM), subject to the other restrictions in the list
       above .

Documentation

   Full documentation is in the docstrings.

   The documentation in the web pages is in need of reorganisation at the
   moment, after the merge of ClientCookie into mechanize.

Credits

   Thanks to all the too-numerous-to-list people who reported bugs and
   provided patches. Also thanks to Ian Bicking, for persuading me that a
   UserAgent class would be useful, and to Ronald Tschalar for advice on
   Netscape cookies.

   A lot of credit must go to Gisle Aas, who wrote libwww-perl, from which
   large parts of mechanize originally derived, and Andy Lester for the
   original, [7]WWW::Mechanize . Finally, thanks to the
   (coincidentally-named) Johnny Lee for the MSIE CookieJar Perl code from
   which mechanize's support for that is derived.

To do

   Contributions welcome!

   The documentation to-do list has moved to the new "docs-in-progress"
   directory in SVN.

   This is very roughly in order of priority
     * Test .any_response() two handlers case: ordering.
     * Test referer bugs (frags and don't add in redirect unless orig req
       had Referer)
     * Remove use of urlparse from _auth.py.
     * Proper XHTML support!
     * Fix BeautifulSoup support to use a single BeautifulSoup instance
       per page.
     * Test BeautifulSoup support better / fix encoding issue.
     * Support BeautifulSoup 3.
     * Add another History implementation or two and finalise interface.
     * History cache expiration.
     * Investigate possible leak further (see Balazs Ree's list posting).
     * Make EncodingFinder public, I guess (but probably improve it
       first). (For example: support Mark Pilgrim's universal encoding
       detector?)
     * Add two-way links between BeautifulSoup & ClientForm object models.
     * In 0.2: switch to Python unicode strings everywhere appropriate
       (HTTP level should still use byte strings, of course).
     * clean_url(): test browser behaviour. I think this is correct...
     * Use a nicer RFC 3986 join / split / unsplit implementation.
     * Figure out the Right Thing (if such a thing exists) for %-encoding.
     * How do IRIs fit into the world?
     * IDNA -- must read about security stuff first.
     * Unicode support in general.
     * Provide per-connection access to timeouts.
     * Keep-alive / connection caching.
     * Pipelining??
     * Content negotiation.
     * gzip transfer encoding (there's already a handler for this in
       mechanize, but it's poorly implemented ATM).
     * proxy.pac parsing (I don't think this needs JS interpretation)
     * Topological sort for handlers, instead of .handler_order attribute.
       Ordering and other dependencies (where unavoidable) should be
       defined separate from handlers themselves. Add new build_opener and
       deprecate the old one? Actually, _useragent is probably not far off
       what I'd have in mind (would just need a method or two and a base
       class adding I think), and it's not a high priority since I guess
       most people will just use the UserAgent and Browser classes.

Getting mechanize

   You can install the [8]old-fashioned way, or using [9]EasyInstall. I
   recommend the latter even though EasyInstall is still in alpha, because
   it will automatically ensure you have the necessary dependencies,
   downloading if necessary.

   [10]Subversion (SVN) access is also available.

   Since EasyInstall is new, I include some instructions below, but
   mechanize follows standard EasyInstall / setuptools conventions, so you
   should refer to the [11]EasyInstall and [12]setuptools documentation if
   you need more detailed or up-to-date instructions.

EasyInstall / setuptools

   The benefit of EasyInstall and the new setuptools-supporting setup.py
   is that they grab all dependencies for you. Also, using EasyInstall is
   a one-liner for the common case, to be compared with the usual
   download-unpack-install cycle with setup.py.

Using EasyInstall to download and install mechanize

    1. [13]Install easy_install
    2. easy_install mechanize

   If you're on a Unix-like OS, you may need root permissions for that
   last step (or see the [14]EasyInstall documentation for other
   installation options).

   If you already have mechanize installed as a [15]Python Egg (as you do
   if you installed using EasyInstall, or using setup.py install from
   mechanize 0.0.10a or newer), you can upgrade to the latest version
   using:
easy_install --upgrade mechanize

   You may want to read up on the -m option to easy_install, which lets
   you install multiple versions of a package.

Using EasyInstall to download and install the latest in-development (SVN
HEAD) version of mechanize

easy_install "mechanize==dev"

   Note that that will not necessarily grab the SVN versions of
   dependencies, such as ClientForm: It will use SVN to fetch dependencies
   if and only if the SVN HEAD version of mechanize declares itself to
   depend on the SVN versions of those dependencies; even then, those
   declared dependencies won't necessarily be on SVN HEAD, but rather a
   particular revision. If you want SVN HEAD for a dependency project, you
   should ask for it explicitly by running easy_install "projectname=dev"
   for that project.

   Note also that you can still carry on using a plain old SVN checkout as
   usual if you like.

Using setup.py from a .tar.gz, .zip or an SVN checkout to download and
install mechanize

   setup.py should correctly resolve and download dependencies:
python setup.py install

   Or, to get access to the same options that easy_install accepts, use
   the easy_install distutils command instead of install (see python
   setup.py --help easy_install)
python setup.py easy_install mechanize

Download

   All documentation (including this web page) is included in the
   distribution.

   This is a stable release.

   Development release.
     * [16]mechanize-0.1.10.tar.gz
     * [17]mechanize-0.1.10.zip
     * [18]Change Log (included in distribution)
     * [19]Older versions.

   For old-style installation instructions, see the INSTALL file included
   in the distribution. Better, [20]use EasyInstall.

Subversion

   The [21]Subversion (SVN) trunk is
   [22]http://codespeak.net/svn/wwwsearch/mechanize/trunk, so to check out
   the source:
svn co http://codespeak.net/svn/wwwsearch/mechanize/trunk mechanize

Tests and examples

Examples

   The examples directory in the [23]source packages contains a couple of
   silly, but working, scripts to demonstrate basic use of the module.
   Note that it's in the nature of web scraping for such scripts to break,
   so don't be too suprised if that happens - do let me know, though!

   It's worth knowing also that the examples on the [24]ClientForm web
   page are useful for mechanize users, and are now real run-able scripts
   rather than just documentation.

Functional tests

   To run the functional tests (which do access the network), run the
   following command:
python functional_tests.py

Unit tests

   Note that ClientForm (a dependency of mechanize) has its own unit
   tests, which must be run separately.

   To run the unit tests (none of which access the network), run the
   following command:
python test.py

   This runs the tests against the source files extracted from the
   package. For help on command line options:
python test.py --help

See also

   There are several wrappers around mechanize designed for functional
   testing of web applications:
     * [25]zope.testbrowser (or [26]ZopeTestBrowser, the standalone
       version).
     * [27]twill.

   Richard Jones' [28]webunit (this is not the same as Steven Purcell's
   [29]code of the same name). webunit and mechanize are quite similar. On
   the minus side, webunit is missing things like browser history,
   high-level forms and links handling, thorough cookie handling, refresh
   redirection, adding of the Referer header, observance of robots.txt and
   easy extensibility. On the plus side, webunit has a bunch of utility
   functions bound up in its WebFetcher class, which look useful for
   writing tests (though they'd be easy to duplicate using mechanize). In
   general, webunit has more of a frameworky emphasis, with aims limited
   to writing tests, where mechanize and the modules it depends on try
   hard to be general-purpose libraries.

   There are many related links in the [30]General FAQ page, too.

FAQs - pre install

     * Which version of Python do I need?
       Python 2.4, 2.5 or 2.6.
     * What else do I need?
       mechanize depends on [31]ClientForm.
     * Does mechanize depend on BeautifulSoup? No. mechanize offers a few
       (still rather experimental) classes that make use of BeautifulSoup,
       but these classes are not required to use mechanize. mechanize
       bundles BeautifulSoup version 2, so that module is no longer
       required. A future version of mechanize will support BeautifulSoup
       version 3, at which point mechanize will likely no longer bundle
       the module.
       The versions of those required modules are listed in the setup.py
       for mechanize (included with the download). The dependencies are
       automatically fetched by [32]EasyInstall (or by [33]downloading a
       mechanize source package and running python setup.py install). If
       you like you can fetch and install them manually, instead - see the
       INSTALL.txt file (included with the distribution).
     * Which license?
       mechanize is dual-licensed: you may pick either the [34]BSD
       license, or the [35]ZPL 2.1 (both are included in the
       distribution).

FAQs - usage

     * I'm not getting the HTML page I expected to see.
          + [36]Debugging tips
          + [37]More tips
     * I'm sure this page is HTML, why does mechanize.Browser think
       otherwise?
b = mechanize.Browser(
    # mechanize's XHTML support needs work, so is currently switched off.  If
    # we want to get our work done, we have to turn it on by supplying a
    # mechanize.Factory (with XHTML support turned on):
    factory=mechanize.DefaultFactory(i_want_broken_xhtml_support=True)
    )

   I prefer questions and comments to be sent to the [38]mailing list
   rather than direct to me.

   [39]John J. Lee, December 2008.
     __________________________________________________________________

   [40]Home
   [41]General FAQs
   mechanize
   [42]mechanize docs
   [43]ClientForm
   [44]ClientCookie
   [45]ClientCookie docs
   [46]pullparser
   [47]DOMForm
   [48]python-spidermonkey
   [49]ClientTable
   [50]1.5.2 urllib2.py
   [51]1.5.2 urllib.py
   [52]Examples
   [53]Compatibility
   [54]Documentation
   [55]To-do
   [56]Download
   [57]Subversion
   [58]More examples
   [59]FAQs

References

   1. http://sourceforge.net/
   2. http://search.cpan.org/dist/WWW-Mechanize/
   3. file://localhost/tmp/ClientForm/
   4. http://www.robotstxt.org/wc/norobots.html
   5. file://localhost/tmp/tmpg4nYYM/#tests
   6. file://localhost/tmp/tmpg4nYYM/doc.html#seekable
   7. http://search.cpan.org/dist/WWW-Mechanize/
   8. file://localhost/tmp/tmpg4nYYM/#source
   9. http://peak.telecommunity.com/DevCenter/EasyInstall
  10. file://localhost/tmp/tmpg4nYYM/#svn
  11. http://peak.telecommunity.com/DevCenter/EasyInstall
  12. http://peak.telecommunity.com/DevCenter/setuptools
  13. http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install
  14. http://peak.telecommunity.com/DevCenter/EasyInstall
  15. http://peak.telecommunity.com/DevCenter/PythonEggs
  16. file://localhost/tmp/tmpg4nYYM/src/mechanize-0.1.10.tar.gz
  17. file://localhost/tmp/tmpg4nYYM/src/mechanize-0.1.10.zip
  18. file://localhost/tmp/tmpg4nYYM/src/ChangeLog.txt
  19. file://localhost/tmp/tmpg4nYYM/src/
  20. file://localhost/tmp/tmpg4nYYM/#download
  21. http://subversion.tigris.org/
  22. http://codespeak.net/svn/wwwsearch/mechanize/trunk#egg=mechanize-dev
  23. file://localhost/tmp/tmpg4nYYM/#source
  24. file://localhost/tmp/ClientForm/
  25. http://cheeseshop.python.org/pypi?:action=display&name=zope.testbrowser
  26. http://cheeseshop.python.org/pypi?%3Aaction=display&name=ZopeTestbrowser
  27. http://www.idyll.org/~t/www-tools/twill.html
  28. http://mechanicalcat.net/tech/webunit/
  29. http://webunit.sourceforge.net/
  30. file://localhost/tmp/bits/GeneralFAQ.html
  31. file://localhost/tmp/ClientForm/
  32. http://peak.telecommunity.com/DevCenter/EasyInstall
  33. file://localhost/tmp/tmpg4nYYM/#source
  34. http://www.opensource.org/licenses/bsd-license.php
  35. http://www.zope.org/Resources/ZPL
  36. http://wwwsearch.sourceforge.net/mechanize/doc.html#debugging
  37. http://wwwsearch.sourceforge.net/bits/GeneralFAQ.html
  38. http://lists.sourceforge.net/lists/listinfo/wwwsearch-general
  39. mailto:jjl@pobox.com
  40. file://localhost/tmp
  41. file://localhost/tmp/bits/GeneralFAQ.html
  42. file://localhost/tmp/mechanize/doc.html
  43. file://localhost/tmp/ClientForm/
  44. file://localhost/tmp/ClientCookie/
  45. file://localhost/tmp/ClientCookie/doc.html
  46. file://localhost/tmp/pullparser/
  47. file://localhost/tmp/DOMForm/
  48. file://localhost/tmp/python-spidermonkey/
  49. file://localhost/tmp/ClientTable/
  50. file://localhost/tmp/bits/urllib2_152.py
  51. file://localhost/tmp/bits/urllib_152.py
  52. file://localhost/tmp/tmpg4nYYM/#examples
  53. file://localhost/tmp/tmpg4nYYM/#compatnotes
  54. file://localhost/tmp/tmpg4nYYM/#docs
  55. file://localhost/tmp/tmpg4nYYM/#todo
  56. file://localhost/tmp/tmpg4nYYM/#download
  57. file://localhost/tmp/tmpg4nYYM/#svn
  58. file://localhost/tmp/tmpg4nYYM/#tests
  59. file://localhost/tmp/tmpg4nYYM/#faq
