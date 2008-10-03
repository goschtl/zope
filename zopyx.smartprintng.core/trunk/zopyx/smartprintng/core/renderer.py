##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


import os
import random
import tempfile
import urlparse
import urllib2
import PIL.Image
import cStringIO

from BeautifulSoup import BeautifulSoup

import zope.component
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements, implementedBy
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from resources import Resource
from interfaces import IImageFetcher
from logger import LOG

class Renderer(object):

    def __init__(self, context=None):
        self.id = str(random.random())
        self.context = context
        self.tempdir = os.path.join(tempfile.gettempdir(), 'smartprinting', self.id)
        LOG.debug('New renderer session: %s' % self.id)
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)


    def render(self, 
               html, 
               template=None,
               resource=None,
               styles=[],
               transformations=[],
               transformation_options={},
               template_options={},
               beautify_html=False,
               ):
        """ 'html' - HTML snippet to be rendered
            'template' - either a filename of pagetemplate or a 
                         ViewPageTemplateFile instance
            'resource' - an instance of resource.Resource
            'styles' - a list of style names to be passed down as full 
                       expanded stylesheet files to the template engine.
                       The name of the style reference to the 'styles'
                       value within the given 'resource' parameter. This
                       option can only be used with a valid 'resource'
                       parameter.
            'transformations' - a list or registered transformation names
            'transformation_options' - options passed down to the specific
                         transformations as specified in 'transformations'.
                         This parameter is a dict of dicts where the keys 
                         reference a transformation name and the value is 
                         the related parameter dict for each transformation.
            'template_options' - an options dictionary passed directly
                        to the template

            Note: using 'template' and 'resource' a mutually-exclusive
        """

        if template is None and resource is None:
            raise ValueError('"resource" and "template" parameters can not be both None')

        if template is not None and resource is not None:
            raise ValueError('Using "resource" and "template" is mutually-exclusive')

        if styles and not resource:
            raise ValueError('Using "styles" without setting "resource" is not possible') 
    
        # The rendering template is either passed directly....
        if template is not None:
            if isinstance(template, str):
                template = PageTemplateFile(template)
        else:
            # or taken from the resource
            template = PageTemplateFile(resource.template_filename)
        assert isinstance(template, PageTemplateFile), 'not a PageTemplateFile'

        if not isinstance(transformations, (list, tuple)):
            raise TypeError('"transformations" must be list/tuple of strings')

        # proceed with transformations based on BeautifulSoup
        soup = BeautifulSoup(html)

        for name in transformations:
            params = transformation_options.get(name, {})
            try:
                T = zope.component.createObject(name, soup=soup, **params)
            except ComponentLookupError:
                raise ValueError('Transformation "%s" is not registred' % name)
            T.transform()
            soup = T.soup

        # Download remote images and make them local 
        # ATT: handling of local images
        soup = self.makeImagesLocal(soup)

        # now pass the modified HTML fragment to the template
        # in order to render a proper HTML document
        html2 = soup.renderContents()
        stylesheets = dict()
        for style in styles:
            try:
                stylesheet_filename = resource.styles[style]
            except KeyError:
                raise ValueError('No style with name "%s" configured' % style)
            stylesheets[style] = '\n%s\n' % file(stylesheet_filename, 'rb').read()

        params = {'body' : unicode(html2, 'utf-8'), 
                  'stylesheets' : stylesheets,
                 }
        params.update(template_options)
        rendered_html = template(**params)
        if beautify_html:
            rendered_html = BeautifulSoup(rendered_html).prettify()
        self.rendered_html = rendered_html
        return self.rendered_html


    def save(self, output_filename=None):
        """ Save rendered html to the filesystem"""

        if output_filename is None:
            output_filename = os.path.join(self.tempdir, 'index.html')
        file(output_filename, 'wb').write(self.rendered_html)
        LOG.debug('HTML written to %s' % output_filename)
        return output_filename


    def makeImagesLocal(self, soup):
        """ All referencered images (local/remote) must be downloaded
            or obtained and put as local copies into the renderers
            working directory.
        """
        
        for img in soup.findAll('img'):
            src = img['src'].encode('ascii', 'ignore')
            try:
                image_path = self._fetchImage(src)
                img['src'] = image_path
            except Exception, e:
                LOG.error('Error handling image (%s)' % e, exc_info=True)
                # remove image from soup since we can handle # the error on our
                # own
                img.extract() 
        return soup


    def _fetchImage(self, src):

        # Image fetching is delegated to an adapter
        image_fetcher = IImageFetcher(self.context, None)
        if not image_fetcher:
            raise ValueError('No adapter for IImageFetcher found')

        img_data = image_fetcher.fetch(src)
        if not img_data:
            raise ValueError('No image data found for %s' % img)

        # We got hold of the image data. Now convert it to PNG and save it
        # within working directory of the renderer.  We convert always to PNG
        # in order to support *all* external converters because they support
        # different image types.
        new_img_path = '%s/%s.png' % (self.tempdir, random.random())
        pil_img = PIL.Image.open(cStringIO.StringIO(img_data))
        pil_img.save(new_img_path, 'PNG')
        del pil_img
        LOG.debug('Image %s stored as %s' % (src, new_img_path))
