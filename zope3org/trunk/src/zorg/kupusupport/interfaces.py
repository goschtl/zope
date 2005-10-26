##############################################################################
#
# Copyright (c) 2003-2004 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Zope3 isar sprint sample integration

$Id: interfaces.py 7083 2004-10-21 15:56:05Z dhuber $
"""

from zope.interface import Interface
from zope.i18nmessageid import MessageIDFactory

from zope.app.container.interfaces import IReadContainer

_ = MessageIDFactory("kupu")


class IKupuEditable(Interface):
    """Mark content object which should be editable by kupu."""


class IKupuPolicy(Interface):
    """Save the kupu editor content to the content object."""

    def update(kupu=None):
        """Update the content object using the kupu editor output.

        """

    def display():
        """Display the kupu specific editor content."""


class IImageReadContainer(IReadContainer):
    """A container that contains only IImage's"""


class IImageLibrary(Interface):
    """Mark content object which might be image libraries."""


class IImageLibraryInfo(Interface):
    """List available images and image libraries."""

    def libraryInfos():
        """List available image library infos.
        
        **Return value**
        dict -- the following keys are provided: 
            'name': id or name of object
            'title': title of the image
            'description': description of the image
            'url': url of the image

        """       

    def imageInfos():
        """List available image infos.
        
        **Return value**
        dict -- the following keys are provided: 
            'name': id or name of object
            'title': title of the image
            'description': description of the image
            'width': width of the image in pixels
            'height': height of the image in pixels
            'size': size in kB, exp. 12kB
            'url': url of the image

        """
