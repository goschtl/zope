# -*- coding: latin-1 -*-
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
"""Tag test setup

$Id$
"""
__docformat__ = "reStructuredText"

import cgi
import cStringIO
import doctest
import os
import unittest
import urllib

try:
    from zope.testing.doctestunit import DocFileSuite
except ImportError:
    from doctest import DocFileSuite

API_KEY = u'ffd1eeacf227a6c9471c5b6d24ad77099'
SECRET = u'ff4cffbe4d209ec4'
FROB = u'2572639-8aac54751ebab5a7'
TOKEN = u'909163-79a56fd4b2ca4a76'
MINI_TOKEN = u'909-a16-3fa'

responses = {
    # flickr.auth
    ('auth.getFrob', ('api_key='+API_KEY,)): 'auth.getFrob-1.txt',
    ('auth.getToken', ('api_key='+API_KEY, 'frob='+FROB)):
        'auth.getToken-1.txt',
    ('auth.checkToken', ('api_key='+API_KEY, 'auth_token='+TOKEN)):
        'auth.checkToken-1.txt',
    ('auth.getFullToken', ('api_key='+API_KEY, 'mini_token=909a163fa')):
        'auth.getFullToken-1.txt',

    # flickr.blogs
    ('blogs.getList', ('api_key='+API_KEY, 'auth_token='+TOKEN)):
        'blogs.getList-1.txt',

    # flickr.contacts
    ('contacts.getList', ('api_key='+API_KEY, 'auth_token='+TOKEN)):
        'contacts.getList-1.txt',
    ('contacts.getList',
     ('api_key='+API_KEY, 'auth_token='+TOKEN, 'filter=friends')):
        'contacts.getList-2.txt',
    ('contacts.getList',
     ('api_key='+API_KEY, 'auth_token='+TOKEN, 'filter=family')):
        'contacts.getList-3.txt',
    ('contacts.getPublicList', ('api_key='+API_KEY, 'user_name=lovelyflickr')):
        'contacts.getPublicList-1.txt',

    # flickr.favorites

    # flickr.photos
    ('photos.search', ('api_key='+API_KEY, u'tags=dornbirn')):
        'photos.search-1.txt',
    ('photos.search', ('api_key='+API_KEY, u'tags=Österreich')):
        'photos.search-2.txt',

    # flickr.test
    ('test.echo', ('api_key='+API_KEY, 'foo=bar')): 'test.echo-1.txt',
    ('test.echo', ('api_key=bullshit',)): 'test.echo-2.txt',
    ('test.login', ('api_key='+API_KEY, 'auth_token='+TOKEN)):
        'test.login-1.txt',
    }

def urlopen(url, data=None):
    if '?' in url and not url.endswith('?'):
        qs = url.split('?')[1]
        key = dict([
            (name, value[0])
            for (name, value) in cgi.parse_qs(qs).items() ])
    else:
        fs = cgi.FieldStorage(
            cStringIO.StringIO(data), environ={'REQUEST_METHOD': 'POST'})
        key = dict([(field.name, field.value) for field in fs.list])

    method = key['method'][7:]
    del key['method']
    if 'api_sig' in key:
        del key['api_sig']
    key = ['='.join(item) for item in sorted(key.items())]
    fn = responses.get((method, tuple(key)), 'success.txt')
    # For testing
    if fn == 'success.txt':
        sig = (method, tuple(key))
        #import pdb; pdb.set_trace()
        pass
    fn = os.path.join(os.path.dirname(__file__), fn)
    return open(fn, 'r')

def setUp(test):
    from lovely.flickr import auth, flickr
    auth.APIAuth._authenticate_for_real = False
    flickr.APIFlickr._urlopen = urlopen
    test.globs.update(
        {'API_KEY': API_KEY, 'SECRET': SECRET, 'FROB': FROB, 'TOKEN': TOKEN})

def tearDown(test):
    from lovely.flickr import auth, flickr
    auth.APIAuth._authenticate_for_real = True
    flickr.APIFlickr._urlopen = urllib.urlopen



def test_suite():
    return unittest.TestSuite((
        DocFileSuite('../README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('../auth.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('../online.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('../blogs.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('../contacts.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        #DocFileSuite('../favorites.txt',
        #             setUp=setUp, tearDown=tearDown,
        #             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        #             ),
        DocFileSuite('../photos.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('../test.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
