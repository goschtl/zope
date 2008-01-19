from Products.Archetypes.public import Schema
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import ImageField
from Products.Archetypes.public import TextField
from Products.Archetypes.public import AnnotationStorage
from Products.validation import V_REQUIRED
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.configuration import zconf
from zopeorg.theme import MessageFactory as _
from zopeorg.theme.config import PROJECTNAME

FeatureSchema = ATDocumentSchema.copy() + Schema((
    TextField("blurb",
              required=True,
              searchable=True,
              primary=False,
              storage = AnnotationStorage(migrate=True),
              validators = ("isTidyHtmlWithCleanup",),
              default_output_type = "text/x-html-safe",
              widget = RichWidget(
                        label = _(u"label_blurb", default=u"Blurb"),
                        description = _(u"help_blurb",
                            default=u"The blurb text is displayed at the top "
                                    u"of the feature page."),
                        rows = 5,
                        allow_file_upload = False),
    ),
    ImageField("image",
        required = False,
        storage = AnnotationStorage(migrate=True),
        languageIndependent = True,
        max_size = zconf.ATNewsItem.max_image_dimension,
        sizes= {"large"   : (768, 768),
                "preview" : (400, 400),
                "mini"    : (200, 200),
                "thumb"   : (128, 128),
                "tile"    :  (64, 64),
                "icon"    :  (32, 32),
                "listing" :  (16, 16),
               },
        validators = (("isNonEmptyFile", V_REQUIRED),
                             ("checkNewsImageMaxSize", V_REQUIRED)),
        widget = ImageWidget(
            label= _(u"label_feature_image",
                default=u"Image"),
            description = _(u"help_feature_image",
                default=u"Will be shown next to the blurb."),
            show_content_type = False)
    ),
    TextField("divider",
              required=False,
              searchable=False,
              primary=False,
              storage = AnnotationStorage(migrate=True),
              validators = ("isTidyHtmlWithCleanup",),
              default_output_type = "text/x-html-safe",
              widget = RichWidget(
                        label = _(u"label_divider",
                            default=u"Divider line"),
                        description = _(u"help_divider",
                            default=u"The divider is shown in a bar between "
                                    u"the blurb and the main context."),
                        rows = 5,
                        allow_file_upload = False),
    ),
    ))

FeatureSchema.moveField("blurb", after="description")
FeatureSchema.moveField("image", after="blurb")


class Feature(ATDocument):
    schema = FeatureSchema

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales. Copied from ATNewsItem.
        """
        if name.startswith("image"):
            field = self.getField("image")
            image = None
            if name == "image":
                image = field.getScale(self)
            else:
                scalename = name[len("image_"):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or "" for empty images
                return image

        return ATDocument.__bobo_traverse__(self, REQUEST, name)

registerATCT(Feature, PROJECTNAME)

