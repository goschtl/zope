"""Widget implementations for rich-text fields.

"""
__docformat__ = "reStructuredText"

import zope.app.form.browser

import zc.resourcelibrary


class FckeditorWidget(zope.app.form.browser.TextAreaWidget):

    editorWidth = 600
    editorHeight = 400

    configurationPath = "/@@/zope_fckconfig.js"
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
            "config": self.configurationPath,
            "name": self.name,
            "shortname": self.name.split('.', 1)[-1],
            "toolbars": self.toolbarConfiguration,
            "width": self.editorWidth,
            "height": self.editorHeight,
            }
        textarea = super(FckeditorWidget, self).__call__()
        return textarea + (self.javascriptTemplate % d)


    # This uses a hard-coded width instead of a percentage, because
    # the percentage doesn't seem to work in Firefox/Mozilla/Epiphany.
    # Hopefully this will be fixed or there's some better workaround
    # for it.

    javascriptTemplate = '''
<script type="text/javascript" language="JavaScript">
var oFCKeditor_%(shortname)s = new FCKeditor(
        "%(name)s", %(width)d, %(height)d, "%(toolbars)s");
    oFCKeditor_%(shortname)s.BasePath = "/@@/fckeditor/";
    oFCKeditor_%(shortname)s.Config["CustomConfigurationsPath"] = "%(config)s";
    oFCKeditor_%(shortname)s.ReplaceTextarea();
</script>
'''
