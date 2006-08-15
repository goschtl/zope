"""Widget implementations for rich-text fields.

"""
__docformat__ = "reStructuredText"

import zope.app.form.browser

import zc.resourcelibrary


class FckeditorWidget(zope.app.form.browser.TextAreaWidget):

    toolbarConfiguration = "zope"

    def __call__(self):
        zc.resourcelibrary.need("fckeditor")
        #
        # XXX The 'shortname' here needs some salt to ensure that
        # multiple widgets with the same trailing name are
        # distinguishable; some encoding of the full name seems
        # appropriate, or a per-request counter would also do nicely.
        #
        d = {
            "name": self.name,
            "shortname": self.name.split('.', 1)[-1],
            "toolbars": self.toolbarConfiguration,
            }
        # suppress the rows/cols since those are ignored anyway
        self.width = 10
        self.height = 10
        textarea = super(FckeditorWidget, self).__call__()
        textarea = textarea.replace(' cols="10"', "", 1)
        textarea = textarea.replace(' rows="10"', "", 1)

        return textarea + (JAVASCRIPT_TEMPLATE % d)


# This uses a hard-coded width instead of a percentage, because the
# percentage doesn't seem to work in Firefox/Mozilla/Epiphany.
# Hopefully this will be fixed or there's some better workaround for
# it.

JAVASCRIPT_TEMPLATE = '''
<script type="text/javascript" language="JavaScript">
var oFCKeditor_%(shortname)s = new FCKeditor("%(name)s", 600, 400, "%(toolbars)s");
    oFCKeditor_%(shortname)s.BasePath = "/@@/fckeditor/";
    oFCKeditor_%(shortname)s.Config["CustomConfigurationsPath"] = "/@@/zope_fckconfig.js";
    oFCKeditor_%(shortname)s.ReplaceTextarea();
</script>
'''
