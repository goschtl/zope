##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""View classes for PhotoSlide

$Id: photoslide.py,v 1.3 2004/03/18 18:04:56 philikon Exp $
"""
from datetime import datetime

from zope.app import zapi
from zope.app.container.browser.adding import Adding
from zope.app.form.browser import ListDisplayWidget
from zope.app.publisher.browser import BrowserView
from zope.schema import Choice
from zope.i18n import MessageIDFactory

_ = MessageIDFactory("photo")


class PhotoSlideAdding(Adding):
    """Custom adding view for PhotoSlide objects."""
    menu_id = "add_photoslide"

class PhotoSlideFolderAdding(Adding):
    """Custom adding view for PhotoSlideFolder objects."""
    menu_id = "add_photoslidefolder"


class PhotoSlideViewBase(BrowserView):
    """Photo Slide View base class.

    Defines some helper functions for all sub-classes.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._setAttributes(request)

    def getPhotoURL(self, photo, display=None):
        """Returns the relative URL of the current photo"""
        photo_name = self._getPhotoName(photo)
        
        if hasattr(self, 'rq_display') and self.rq_display and not display:
            display = self.rq_display
        if display:    
            return "%s?display=%s" % (photo_name, display)
        else:
            return photo_name 

    def _setAttributes(self, request):
        """Sets all attributes in request to local attributes."""
        for attr in ('page', 'display'):
            if attr in request:
                setattr(self, 'rq_' + attr, request[attr])

    def _getPhotoName(self, photo):
        return zapi.getName(photo)

    def _createUrl(self, pageName, **kw):
        """Returns the page name concatenated with it's needed parameters.
        The value of each parameter is fetch from self, though it can
        be overidden by passing it along as a keyword argument.
        """
        paramDict = kw
        # put all parameters in paramDict
        for param in ('page', 'display'):
            if param not in paramDict and getattr(self, 'rq_'+param):
                paramDict[param] = getattr(self, 'rq_'+param)
        # build the url
        url = pageName + '?'
        for name, value in paramDict.items():
            if url[len(url)-1] != '?':
                url += '&'
            url += name + '=' + str(value)
        return url
    

class PhotoSlideViewThumbnails(PhotoSlideViewBase):
    """View class for viewThumbnails.html"""

    def getPhotosPage(self):
        """Returns a list of lists of tuples containing the relative
        thumbnail URL and the relative URL the the view page of the
        photo
        """ 
        result = []
        max_col = 3
        row_count = 0
        col_count = 0
        index = 0
        photos = self.context.getPhotos()
        # XXX should be possible to get several pages
        for photo in photos:
            index += 1
            if col_count >= max_col:
                col_count = 0
                row_count += 1
            if col_count == 0:
                result.append([])
            result[row_count].append(('viewPhoto.html?page=%i' % index,
                                      self.getPhotoURL(photo,
                                                       'thumbnail')))
            col_count += 1

        return result


class PhotoSlideViewEditPhotos(PhotoSlideViewBase):
    """View class for editPhotos.html"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        if self.request.get('UPDATE_EDIT_PHOTOS', None):
            changed = False
            orgPositions = self.context.getPhotoNames()
            changedPositions = []
            for name in orgPositions:
                photo = zapi.traverseName(self.context, name,
                                          request=self.request)
                changed = changed or \
                          self._setPhotoAttribute(photo, name, 'title',
                                                  self.request)
                changed = changed or \
                          self._setPhotoAttribute(photo, name, 'description',
                                                  self.request)
                if self._isPositionChanged(name, orgPositions, self.request):
                    changed = True
                    changedPositions.append(name)
            self._setPhotoPositions(changedPositions, self.request)
            if changed:
                formatter = self.request.locale.getDateTimeFormatter('medium')
                result = _("Values updated on ${date_time}")
                # XXX Should probably not use UTC all the time
                result.mapping = {'date_time':
                                  formatter.format(datetime.utcnow())}
            else:
                result = _("Nothing was changed")
            return result

    def _setPhotoAttribute(self, photo, photoName, photoAttr, dict):
        """Sets the photo attribute in case it has changed and is in dict"""
        widgetName = 'photo_%s_%s' % (photoName, photoAttr)
        changed = False
        if widgetName in dict: 
            if getattr(photo, photoAttr) <> dict[widgetName]:
                changed = True
                setattr(photo, photoAttr, dict[widgetName])
        return changed
              
    def _isPositionChanged(self, photoName, orgPositions, dict):
        widgetName = 'photo_%s_position' % photoName
        return orgPositions.index(photoName)+1 != int(dict[widgetName])

    def _setPhotoPositions(self, photoNames, dict):
        """Sets the photo's position in case it has been changed."""
        for name in photoNames:
            widgetName = 'photo_%s_position' % name
            self.context.setPosition(name, dict[widgetName])

    def getPhotoView(self, photo):
        """Returns a view for the photo.

        This way we can re-use the widget's the photo has.
        """
        view = zapi.getView(photo, 'edit.html', self.request)
        photoName = self._getPhotoName(photo)

        # Add a positions widget
        field = Choice(
            __name__='position',
            title=u'Pos',
            description=u'The position of the photo.',
            values=range(1, len(self.context)+1),
            default=self.context.getPosition(photoName)
            )
        view.position_widget = ListDisplayWidget( field,range(1, len(self.context)+1), self.request)
        pos = self.context.getPosition(photoName)
        view.position_widget.setData(pos)
        # Make the widget's names unique
        view.title_widget.name = 'photo_%s_title' % photoName
        view.position_widget.name = 'photo_%s_position' % photoName
        view.position_widget.size = 1
        view.description_widget.name = 'photo_%s_description' % photoName
        view.description_widget.height = 5
        
        return view



class PhotoSlideViewPhoto(PhotoSlideViewBase):
    """View class for viewPhoto.html"""
    rq_page = 1
    rq_display = None

    def __init__(self, context, request):
        super(PhotoSlideViewPhoto, self).__init__(context, request)
        self.rq_page = int(self.rq_page)

    def getNumberOfPhotos(self):
        """Returns the number of photos in the photo slide."""
        return self.context.__len__()

    def getCurrentDisplayId(self):
        """Returns the display id that's being used."""
        if self.rq_display:
            return self.rq_display
        else:
            photo = self.getCurrentPhoto()
            return photo.currentDisplayId

    def getDisplayIds(self):
        """Returns a list of tuples consisting of the display id and
        the relative URL to it's view page.
        It returns all display ids found in the current photo, except
        the thumbnail.
        It sorts them by their size, smallest first.
        """
        photo = self.getCurrentPhoto()
        dispIds = list(photo.getDisplayIds())
        dispIds.remove('thumbnail')
        # XXX should consider the size with regards to aspect ratio
        dispIds.sort(
            lambda x,y:
            photo.getDisplaySize(x)[0].__cmp__(photo.getDisplaySize(y)[0]))
        result = map(lambda dispId: (dispId, self._createUrl('viewPhoto.html',
                                                    display=dispId)),
                     dispIds)
        return result

    def getPageURLs(self):
        """Returns a list of tuples consisting of the position of the
        page and the URL to it
        """
        startPage = self.rq_page-4
        endPage = self.rq_page+4
        if startPage < 1:
            endPage += 1 - startPage
            startPage = 1
        if endPage > self.getNumberOfPhotos():
            startPage -= (endPage - self.getNumberOfPhotos())
            endPage = self.getNumberOfPhotos()
        # Last check
        if startPage < 1:
            startPage = 1

        names = self.context.getPhotoNames()
        names = names[startPage-1:endPage-1]
        positions = range(startPage, endPage+1)
        urls = map(lambda pos: self._createUrl('viewPhoto.html', page=pos),
                   positions)

        return zip(positions, urls)

    def getNextURL(self):
        """Returns the URL to the next page"""
        url = self._createUrl('viewPhoto.html', page=self.rq_page+1)
        return url

    def getPreviousURL(self):
        """Returns the URL to the previous page"""
        url = self._createUrl('viewPhoto.html', page=self.rq_page-1)
        return url


    def isFirstPhoto(self):
        """Returns true iff the current photo is the first one"""
        return self.rq_page == 1

    def isLastPhoto(self):
        """Returns true iff the current photo is the last one"""
        return self.rq_page == self.getNumberOfPhotos()

    def getCurrentPhoto(self):
        """Returns the photo with position self.rq_page"""
        photos = self.context.getPhotoNames()
        return  zapi.traverseName(self.context,
                                  photos[self.rq_page-1],
                                  request=self.request)
