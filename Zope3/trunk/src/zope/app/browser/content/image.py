##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Define view component for naive file editing.

$Id: image.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""

from zope.app.browser.content.file import FileUpload
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.event import publish
from zope.publisher.browser import BrowserView


class ImageData(BrowserView):

    def __call__(self):
        image = self.context
        if self.request is not None:
            self.request.response.setHeader('content-type',
                                            image.getContentType())
        return image.getData()

    def tag(self, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, css_class=None, **args):
        """
        Generate an HTML IMG tag for this image, with customization.
        Arguments to self.tag() can be any valid attributes of an IMG tag.
        'src' will always be an absolute pathname, to prevent redundant
        downloading of images. Defaults are applied intelligently for
        'height', 'width', and 'alt'. If specified, the 'scale', 'xscale',
        and 'yscale' keyword arguments will be used to automatically adjust
        the output height and width values of the image tag.

        Since 'class' is a Python reserved word, it cannot be passed in
        directly in keyword arguments which is a problem if you are
        trying to use 'tag()' to include a CSS class. The tag() method
        will accept a 'css_class' argument that will be converted to
        'class' in the output tag to work around this.
        """
        if width is None:
            width = self.context.getImageSize()[0]
        if height is None:
            height = self.context.getImageSize()[1]

        # Auto-scaling support
        xdelta = xscale or scale
        ydelta = yscale or scale

        if xdelta and width:
            width = str(int(round(int(width) * xdelta)))
        if ydelta and height:
            height = str(int(round(int(height) * ydelta)))

        result = '<img src="%s"' % (self.absolute_url())

        if alt is None:
            alt = getattr(self, 'title', '')
        result = '%s alt="%s"' % (result, alt)

        if height is not None:
            result = '%s height="%s"' % (result, height)

        if width is not None:
            result = '%s width="%s"' % (result, width)

        if not 'border' in [a.lower() for a in args.keys()]:
            result = '%s border="0"' % result

        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)

        for key in args.keys():
            value = args.get(key)
            result = '%s %s="%s"' % (result, key, value)

        return '%s />' % result


class ImageUpload(FileUpload):
    """Image edit view mix-in that provides access to image size info"""

    def size(self):
        sx, sy = self.context.getImageSize()
        return "%s x %s pixels" % (sx > 0 and sx or 0, sx > 0 and sy or 0)

    def apply_update(self, data):
        """Apply user inputs

        These inputs have already been validated.

        Return a boolean indicating whether we changed anything,
        """

        unchanged = True

        # if we can compute the content type from the raw data, then
        # that overrides what the user provided, so set the content
        # type first.

        contentType = data.get('contentType')
        if contentType and contentType != self.context.contentType:
            self.context.contentType = contentType
            unchanged = False

        if 'data' in data:
            self.context.data = data['data']
            unchanged = False

        if not unchanged:
            publish(self.context, ObjectModifiedEvent(self.context))

        return unchanged
