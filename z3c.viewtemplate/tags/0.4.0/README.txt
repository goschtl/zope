This package allows us to separate the registration of the view code and the
view templates.

Why is this a good thing?

While developing customizable applications that require us to develop multiple
customer UIs for one particular application, we noticed there is a fine but
clear distinction between skins and layers. Layers contain the logic to
prepare data for presentation output, namely the view classes. Skins, on the
other hand contain the resources to generate the UI, for example templates,
images and CSS files.

The problem of the existing infrastructure is that code, template and layer
are all hardlinked in one zcml configuration directive of the view component
-- page, content provider, viewlet. This package separates this triplet --
code, template, layer -- into two pairs, code/layer and template/skin. No
additional components are introduced, since skins and layers are physically
the same components.

