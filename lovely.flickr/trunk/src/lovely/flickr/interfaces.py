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
"""this module implements the flickr.photos namespace

http://www.flickr.com/services/api/

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.interface.common import sequence

class FlickrError(Exception):
    """An error occured while executing a Flickr API method."""

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'Flickr Error %i: %s' %(self.code, self.msg.encode('utf-8'))

    def __repr__(self):
        return '<%s %i, %r>' %(self.__class__.__name__, self.code, self.msg)


class IFlickr(zope.interface.Interface):
    """Flickr toplevel namespace"""

    auth = zope.interface.Attribute('flickr.auth package')
    blogs = zope.interface.Attribute('flickr.blogs package')
    photos = zope.interface.Attribute('flickr.photos package')
    test = zope.interface.Attribute('flickr.test package')


class IBaseFlickrObject(zope.interface.Interface):
    """This interface has to be implemented by all Flickr objects"""

    def fromElement(element):
        """Create a Flickr object from the ElementTree element.

        This is a classmethod.
        """


class IUser(IBaseFlickrObject):
    """A Flickr user"""

    nsid = zope.schema.TextLine(
        title = u'User Id',
        description = u'The Flickr user id.',
        required = True
        )

    username = zope.schema.TextLine(
        title = u'Username',
        description = u'The username used to log into Flickr.',
        required = True
        )

    fullname = zope.schema.TextLine(
        title = u'Full name',
        description = u'The full name of the Flickr user.',
        required = True
        )


class IAuth(IBaseFlickrObject):
    """An authentication Response"""

    token = zope.schema.TextLine(
        title = u'Token',
        description = u'The authentication token to be used.',
        required = True
        )

    perms = zope.schema.List(
        title = u'Permissions',
        description = u'A set of permissions for this authentication token.',
        required = True,
        value_type = zope.schema.Choice(
                values=['none', 'read', 'write', 'delete'])
        )

    user = zope.schema.Object(
        title = u'User',
        description = u'The Flickr user for whom the authentication was '
                      u'granted.',
        schema = IUser,
        required = True
        )


class IBlogs(sequence.ISequence):
    """A list of blog entries."""


class IBlog(IBaseFlickrObject):
    """A blog entry on Flickr."""

    id = zope.schema.Int(
        title = u'Id',
        description = u'The Flickr blog id.',
        required = True
        )

    name = zope.schema.TextLine(
        title = u'Name',
        description = u'The Flickr blog name.',
        required = True
        )

    needspassword = zope.schema.Int(
        title = u'Needs Password',
        description = u'Whether the blog needs a password to upload a photo.',
        required = True
        )

    url = zope.schema.TextLine(
        title = u'URL',
        description = u'The Flickr blog URL.',
        required = True
        )


class IContact(IBaseFlickrObject):
    """A single contact."""

    nsid = zope.schema.TextLine(
        title = u'NSID',
        description = u'The id of the contact.',
        required = True
        )

    username = zope.schema.TextLine(
        title = u'Username',
        description = u'The username of the contact.',
        required = True
        )

    iconserver = zope.schema.Int(
        title = u'Icon Server',
        description = u'The id of the server on which the icon is available.',
        required = True
        )

    realname = zope.schema.TextLine(
        title = u'Real Name',
        description = u'The real name of the contact.',
        required = False
        )

    friend = zope.schema.Int(
        title = u'Friend',
        description = u'Specifies whether the contact is a friend.',
        required = False
        )

    family = zope.schema.Int(
        title = u'Family',
        description = u'Specifies whether the contact is a family member.',
        required = False
        )

    ignored = zope.schema.Int(
        title = u'Ignored',
        description = u'Specifies whether the contact is ignored.',
        required = True
        )


class IContacts(IBaseFlickrObject):
    """A collection of contacts."""


class IPhoto(IBaseFlickrObject):
    """A single photo."""

    id = zope.schema.Int(
        title = u'Id',
        description = u'The id of the photo.',
        required = True
        )

    owner = zope.schema.TextLine(
        title = u'Owner',
        description = u'The owner user id of the photo.',
        required = True
        )

    secret = zope.schema.TextLine(
        title = u'Secret',
        description = u'The secret of the photo.',
        required = True
        )

    server = zope.schema.Int(
        title = u'Server',
        description = u'The id of the server on which the photo is available.',
        required = True
        )

    title = zope.schema.TextLine(
        title = u'Title',
        description = u'The title of the photo.',
        required = True
        )

    ispublic = zope.schema.Int(
        title = u'Is Public',
        description = u'Specifies whether the photo is public.',
        required = True
        )

    isfriend = zope.schema.Int(
        title = u'Is Friend',
        description = u'Specifies whether the photo is from a friend.',
        required = True
        )

    isfamily = zope.schema.Int(
        title = u'Is Family',
        description = u'Specifies whether the photo is from a family member.',
        required = True
        )


class IPhotos(IBaseFlickrObject):
    """A sub-collection of photos within a larger collection."""

    page = zope.schema.Int(
        title = u'Page',
        description = u'The page this photos collection describes.',
        required = True
        )

    pages = zope.schema.Int(
        title = u'Pages',
        description = u'The total amount of pages available.',
        required = True
        )

    perpage = zope.schema.Int(
        title = u'Per Page',
        description = u'The amount of photos per page.',
        required = True
        )

    total = zope.schema.Int(
        title = u'Total',
        description = u'The total amount of photos available.',
        required = True
        )


class IAPIFlickr(zope.interface.Interface):
    """This is our base class for all Flickr API classes.

    It provides the basic information to connect to the Flickr services.
    """

    api_key = zope.schema.TextLine(
        title = u'Flickr API Key',
        description = u'Flickr API Key required to use the Flickr API',
        required = True
        )

    secret = zope.schema.TextLine(
        title = u'Flickr Secret',
        description = u'Flickr API Authentication Secret.',
        required = True
        )

    url = zope.schema.TextLine(
        title = u'Flickr API URL',
        description = u'The Flickr API URL to use; '
                      u'usually http://www.flickr.com/services/rest',
        required = True,
        default = u'http://www.flickr.com/services/rest',
        )

    def execute(method, **kw):
        """Send a request to the Flickr Service endpoint and return the result.

        The method will return an ``ElementTree`` data structure.
        """


class IAPIAuth(IAPIFlickr):
    """This class provides a pythonic interface to the ``flickr.auth``
    namespace."""

    def getFrob():
        """Returns a frob to be used during authentication.

        The result will be the frob string.

        See ``http://flickr.com/services/api/flickr.auth.getFrob.html``
        """

    def checkToken(auth_token):
        """Returns the credentials attached to an authentication token.

        The result will be an ``Auth`` instance.

        See ``http://flickr.com/services/api/flickr.auth.checkToken.html``
        """

    def getToken(frob):
        """Returns the auth token for the given frob, if one has been attached.

        The result will be an ``Auth`` instance.

        See ``http://flickr.com/services/api/flickr.auth.getToken.html``
        """

    def getFullToken(mini_token):
        """Get the full authentication token for a mini-token.

        The result will be an ``Auth`` instance.

        See ``http://flickr.com/services/api/flickr.auth.getFullToken.html``
        """

    def getAuthenticationURL(self, frob, perms):
        """Get the Flickr Web site authentication URL.

        The result will be a URL string.

        This is not a Flickr API method. It is provided as a client service.
        """

    def authenticate(self, frob, perms, username, password):
        """Try to authenticate against Flickr and allow the frob.

        This is not a Flickr API method. It is provided as a client service.
        """

    def authenticateCookie(self, frob, perms, cookies):
        """Try to authenticate against Flickr by using the stored cookie

        This is not a Flickr API method. It is provided as a client service.
        """


class IAPIBlogs(IAPIFlickr):
    """This class provides a pythonic interface to the ``flickr.blogs``
    namespace."""

    def getList():
        """Get a list of configured blogs for the calling user.

        The result will be a ``Blogs`` instance.

        See ``http://flickr.com/services/api/flickr.blogs.getList.html``
        """

    def postPhoto(blog_id, photo_id, title, description, blog_password=None):
        """Post a photo on a blog.

        There is no return value.

        See ``http://flickr.com/services/api/flickr.blogs.postPhoto.html``
        """

class IAPIContacts(IAPIFlickr):
    """This class provides a pythonic interface to the ``flickr.contacts``
    namespace."""

    def getList(filter=None):
        """Get a list of contacts for the calling user.

        The result will be a ``Contacts`` instance (list) and contain
        ``Contact`` instances

        See ``http://www.flickr.com/services/api/flickr.contacts.getList.html``
        """

    def getPublicList(user_id):
        """Get the contact list for the given user.

        The result will be a ``Contacts`` instance (list) and contain
        ``Contact`` instances

        See ``http://www.flickr.com
              /services/api/flickr.contacts.getPublicList.html``
        """


class IAPITest(IAPIFlickr):
    """This class provides a pythonic interface to the ``flickr.test``
       namespace."""

    def echo(**kw):
        """Test connectivity to Flickr.

        The result will be an echo of all parameters passed.

        See ``http://www.flickr.com/services/api/flickr.test.echo.html``
        """

    def login():
        """A testing method which checks if the caller is logged in then
        returns their username.

        The result will be an User instance

        See ``http://www.flickr.com/services/api/flickr.test.login.html``
        """

    def null():
        """Null test

        There is no return value.

        See ``http://www.flickr.com/services/api/flickr.test.null.html``
        """


class IAPIPhotos(IAPIFlickr):
    """This class provides a pythonic interface to the ``flickr.photos``
       namespace."""

    def search(user_id=None, tags=None, tag_mode=None, text=None,
               min_upload_date=None, max_upload_date=None, min_taken_date=None,
               max_taken_date=None, license=None, sort=None,
               privacy_filter=None, extras=None, per_page=None, page=None):
        """Return a list of photos matching some criteria.

        Only photos visible to the calling user will be returned. To return
        private or semi-private photos, the caller must be authenticated with
        'read' permissions, and have permission to view the photos.
        Unauthenticated calls will only return public photos.

        See ``http://www.flickr.com/services/api/flickr.photos.search.html``
        """
