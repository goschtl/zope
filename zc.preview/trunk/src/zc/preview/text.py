"""Very simple preview-view for text/plain content.

A more elaborate approach is needed if we care about supporting
specific structured flavors used among programmers, but this is
sufficient for the most basic use.

"""
__docformat__ = "reStructuredText"

import codecs

import zope.formlib.form
import zope.mimetype.interfaces
import zope.mimetype.source
import zope.schema

from i18n import _


class TextPreview(zope.formlib.form.Form):

    actions = ()

    def get_rendered_encoding(self):
        return self.codec

    def get_rendered_text(self):
        return self.text

    encoding_field = zope.formlib.form.Field(
        zope.schema.Choice(
            __name__=_("encoding"),
            title=_("Encoding"),
            description=_("Character data encoding"),
            source=zope.mimetype.source.codecSource,
            required=False,
            ),
        for_display=True,
        get_rendered=get_rendered_encoding,
        )

    text_field = zope.formlib.form.Field(
        zope.schema.Text(
            __name__="text",
            title=_("Text"),
            description=_("The text of the document."),
            required=False,
            ),
        get_rendered=get_rendered_text,
        )

    msgTextEncodingNotSpecified = _(
        "Text encoding not specified and could not be determined.")

    msgErrorDecodingText = _(
        "Specified text encoding does not match data.")

    def __init__(self, context, request):
        # set up fields
        fields = []

        f = context.open("r")
        data = f.read()
        f.close()

        # determine if the text is decodable, or unmarked ASCII
        ci = zope.mimetype.interfaces.IContentInfo(context)
        charset = ci.effectiveParameters.get("charset")
        if not charset:
            # The `IContentInfo` adapter should have gotten this, but
            # if not, we fall back to a simple encoding sniff that
            # only supports a few sure-bet values.  This lets us work
            # with the most common encodings regardless of the
            # software configuration.
            #
            charset = sniffEncoding(data)
            try:
                self.text = unicode(data, charset)
            except UnicodeError:
                self.status = self.msgTextEncodingNotSpecified
                self.have_text = False
            else:
                self.have_text = True
        else:
            try:
                self.text = ci.decode(data)
            except UnicodeError:
                self.status = self.msgErrorDecodingText
                self.have_text = False
            else:
                self.codec = ci.getCodec()
                fields.append(self.encoding_field)
                self.have_text = True

        if self.have_text:
            fields.append(self.text_field)

        self.form_fields = zope.formlib.form.Fields(*fields)
        super(TextPreview, self).__init__(context, request)

    def setUpWidgets(self, ignore_request=False):
        super(TextPreview, self).setUpWidgets(ignore_request=ignore_request)
        if self.have_text:
            w = self.widgets["text"]
            w.extra = 'disabled="disabled"'
            w.cssClass = "display-only"
            w.width = 80


def sniffEncoding(data):
    """Guess what encoding might work to decode `data`.

    The result is considered the 'most likely' candidate, but decoding
    might fail.

    """
    for prefix, charset in _bom_prefix:
        if data.startswith(prefix):
            return charset
    return "ascii"

_bom_prefix = (
    (codecs.BOM_UTF8, "utf-8"),
    (codecs.BOM_UTF16_BE, "utf-16be"),
    (codecs.BOM_UTF16_LE, "utf-16le"),
    )
