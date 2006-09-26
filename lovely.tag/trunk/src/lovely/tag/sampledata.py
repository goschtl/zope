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
"""Sample Data for Tagging

$Id$
"""
import os
import random

from zope import interface
from zope import component
from zope.app.component import hooks

from z3c.sampledata.interfaces import ISampleDataPlugin
from lovely import tag

LOCAL_DIR = os.path.dirname(__file__)

from lovely import tag


def generate(max_tags=100000, engine=None, seed=0):

    rand = random.Random(seed)

    tag_data = file(os.path.join(LOCAL_DIR, 'tags.data'), 'r').read().split()
    tag_data = [unicode(name) for name in tag_data]

    user_data = file(os.path.join(LOCAL_DIR, 'users.data'), 'r').read().split()
    user_data = [unicode(user) for user in user_data]

    if engine is None:
        engine = tag.TaggingEngine()

    cur_tags = 0
    obj_num = 0
    while cur_tags < max_tags:
        obj_num += 1
        user_num = rand.randint(20, 30)
        for user in rand.sample(user_data, user_num):
            tags_num = rand.randint(1, 7)
            cur_tags += tags_num
            tags = rand.sample(tag_data, tags_num)
            engine.update(obj_num, user, tags)

    return engine


class SampleEngine(object):
    interface.implements(ISampleDataPlugin)
    name = 'lovely.tags.sampleengine'
    dependencies = []
    schema = None

    def generate(self, context, param={}, dataSource=None, seed=None):
        hooks.setSite(context)

        engine = component.queryUtility(tag.interfaces.ITaggingEngine)
        if engine is None:
            # Add the tagging engine
            engine = tag.TaggingEngine()
            sm = context.getSiteManager()
            sm['default']['tagging-engine'] = engine
            component.provideUtility(engine, tag.interfaces.ITaggingEngine)
        return engine


class SampleTags(object):
    interface.implements(ISampleDataPlugin)
    name = 'lovely.tags.sampledata'
    dependencies = []
    schema = None

    def generate(self, context, param={}, dataSource=None, seed=None):
        engine = component.getUtility(tag.interfaces.ITaggingEngine)
        return generate(20, engine, seed)

