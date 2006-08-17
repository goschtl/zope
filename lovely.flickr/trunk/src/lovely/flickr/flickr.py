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
"""Flickr Base Class

$Id$
"""
__docformat__ = "reStructuredText"

import cElementTree
import md5
import urllib
from zope.schema import fieldproperty
from lovely.flickr import interfaces


class APIFlickr(object):
    """This is the base class for all Flickr API classes.
    """
    api_key = fieldproperty.FieldProperty(interfaces.IAPIFlickr['api_key'])
    url = fieldproperty.FieldProperty(interfaces.IAPIFlickr['url'])

    # Tests can use this hooks to allow for stub testing.
    _urlopen = urllib.urlopen

    def __init__(self, api_key, secret=None, auth_token=None, url=None):
        self.api_key = api_key
        self.secret = secret
        self.auth_token = auth_token
        if url is not None:
            self.url = url

    def initParameters(self, method, **params):
        params['api_key'] = self.api_key
        params['method'] = method
        return params

    def addAuthToken(self, params):
        '''Add the authentication token to the paramter list'''
        params['auth_token'] = self.auth_token

    def sign(self, params):
        """Sign the Flickr request.

        See http://www.flickr.com/services/api/auth.spec.html, Section 8
        """
        # Step 1: Sort your argument list into alphabetical order based on
        #         the parameter name.
        plist = sorted(params.items())
        # Step 2: Concatenate the shared secret and argument name-value pairs.
        sig = u''.join([name+unicode(value) for name, value in plist])
        sig = self.secret + sig
        # Step 3: Calculate the md5() hash of this string.
        sig_hex = md5.md5(sig).hexdigest()
        # The signature is now complete; add it to the parameter list
        params['api_sig'] = sig_hex

    def execute(self, params, http='GET'):
        """See interfaces.IAPIFlickr"""
        params = dict([(name, unicode(value).encode('UTF-8'))
                       for name, value in params.items()])

        # The function had been converted to a method :-(
        urlopen = self._urlopen.im_func

        if http == 'GET':
            url = '%s/?%s' % (self.url, urllib.urlencode(params))
            rsp = urlopen(url)
        elif http == 'POST':
            rsp = urlopen(self.url, urllib.urlencode(params))
        else:
            raise ValueError('HTTP Verb not recognized')

        tree = cElementTree.parse(rsp).getroot()

        stat = tree.get('stat')
        if stat != 'ok':
            err = tree.find('err')
            raise interfaces.FlickrError(
                code=int(err.get('code')), msg=unicode(err.get('msg')))

        return tree
