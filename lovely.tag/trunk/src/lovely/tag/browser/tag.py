##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Tagging Views

$Id$
"""
__docformat__ = "reStructuredText"

from zope.publisher.browser import BrowserView
from zope import component, schema
from lovely.tag.interfaces import ITaggingEngine, ITagging
from zope.cachedescriptors.property import Lazy
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.formlib import form
from lovely.tag import _
import pytz
import datetime
from zope.interface.common import idatetime


class TaggingMixin(object):

    @Lazy
    def engine(self):
        return component.getUtility(ITaggingEngine)

    @Lazy
    def tagging(self):
        return ITagging(self.context)

    def getCloud(self, maxTags=100):
        """returns a tag cloud"""
        cloud = self.engine.getCloud()
        return normalize(cloud, maxTags)


class TaggingView(BrowserView, TaggingMixin):
    """Show the tags of the context as a cloud"""

    cloud       = ViewPageTemplateFile('tagcloud.pt')
    linkedcloud = ViewPageTemplateFile('linkedtagcloud.pt')

    def __init__(self, context, request):
        super(TaggingView, self).__init__(context, request)


class RelatedView(BrowserView, TaggingMixin):
    """Show related tags as a cloud"""

    cloud       = ViewPageTemplateFile('tagcloud.pt')
    linkedcloud = ViewPageTemplateFile('linkedtagcloud.pt')

    def __init__(self, context, request):
        super(RelatedView, self).__init__(context, request)

    def getCloud(self, tag=None, maxTags=100):
        """returns a tag cloud"""
        if tag is None:
            tag = self.request.get('tagname',None)
        if tag is None:
            return []
        cloud = self.engine.getFrequency(self.engine.getRelatedTags(tag))
        return normalize(cloud, maxTags)


def normalize(cloud, maxTags=100, maxValue=6):
    if len(cloud) == 0:
        return []
    minmax = sorted(cloud, key=lambda i: i[1],reverse=True)

    if maxTags>0:
        end = min(maxTags,len(minmax))
    else:
        end = len(minmax)
    if end == 0:
        return []
    minmax = minmax[:end]
    minFreq = minmax[-1][1]
    maxFreq = minmax[0][1]
    freqRange = maxFreq-minFreq
    if freqRange>0:
        ratio = float(maxValue-1)/freqRange
    else:
        ratio = None
    res = []
    for tag, frequency in sorted(minmax):
        if ratio is None:
            normalized=1
        else:
            normalized = int((frequency-minFreq)*ratio) +1
        res.append(dict(name=tag,
                        normalized=normalized,
                        frequency=frequency,))
    return res


class UserTagForm(form.EditForm, TaggingMixin):

    form_fields = form.Fields(
        schema.TextLine(__name__='tags', title=_("Tags")))

    def setUpWidgets(self, ignore_request=False):
        # override to add existing tags to the field
        tags = u' '.join(self.tagging.getTags(
            [self.request.principal.id]))
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=dict(tags=tags),
            ignore_request=ignore_request
            )

    @form.action(_("Apply"))
    def handle_edit_action(self, action, data):
        tags = data.get('tags','')
        tags = set(tags.split())

        user = self.request.principal.id
        oldTags = self.tagging.getTags(user)
        if oldTags != tags:
            self.tagging.update(user, tags)
            formatter = self.request.locale.dates.getFormatter(
                            'dateTime', 'medium')
            try:
                time_zone = idatetime.ITZInfo(self.request)
            except TypeError:
                time_zone = pytz.UTC
            status = _("Updated on ${date_time}",
                       mapping={'date_time':
                                formatter.format(
                                   time_zone.normalize(datetime.datetime.now())
                                )
                               }
                      )
            self.status = status
        else:
            self.status = _('No changes')


