import time
import pkg_resources
import os
import re
import sys

import Globals
from App.ImageFile import ImageFile, guess_content_type
from App.Common import rfc1123_date
from App.special_dtml import DTMLFile, defaultBindings
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.PageTemplateFile import XML_PREFIX_MAX_LENGTH
from Products.PageTemplates.PageTemplateFile import sniff_type
from zLOG import LOG
from zLOG import ERROR
from Globals import DevelopmentMode

class PageTemplateResource(PageTemplateFile):

    def __init__(self, path, module_globals=None, module=None, **kw):
        """Load a PT from a resource which may be an egg package or a file.
        path is the relative path within the product package. You can provide
        the package module by passing in its globals() dictionary in
        module_globals or you can provide a dotted module path as module
        """
        if module_globals is not None and module is not None:
            raise ValueError(
                "Cannot specify both module_globals and module")
        if module is None:
            if module_globals is not None:
                module = module_globals['__name__']
            else:
                raise ValueError(
                    "Either module_globals or module must be specified")
        self.ZBindings_edit(self._default_bindings)
        name = kw.get('__name__')
        if name:
            self._need__name__ = 0
            self.__name__ = name
        else:
            self.__name__ = os.path.basename(path)
        self.path = path
        self.module = module
        self.zipped = is_zipped(module)
        self.mtime = 0

    def _cook_check(self):
        if self.mtime and not self.zipped and not DevelopmentMode:
            return
        __traceback_info__ = (self.path, self.module)
        f = pkg_resources.resource_stream(self.module, self.path)
        mtime = 0

        if not self.zipped and self.mtime and hasattr(f.name):
            try:
                mtime = os.path.getmtime(f.name)
                if mtime == self.mtime:
                    # File has already been cooked and has not changed
                    return
            except OSError:
                # Can't determine the mod time, Oh well
                pass
        try:
            text = f.read(XML_PREFIX_MAX_LENGTH)
        except:
            f.close()
            raise
        mime_type = sniff_type(text)
        # Punting on reading html in text mode, package resources
        # only supports binary mode via its api
        text += f.read()
        f.close()
        self.pt_edit(text, mime_type)
        self._cook()
        if self._v_errors:
            LOG('PageTemplateFile', ERROR, 'Error in template',
                '\n'.join(self._v_errors))
            return
        self.mtime = mtime


class ImageResource(ImageFile):

    def __init__(self, path, module_globals=None, module=None, **kw):
        if module_globals is not None and module is not None:
            raise ValueError(
                "Cannot specify both module_globals and module")
        if module is None:
            if module_globals is not None:
                module = module_globals['__name__']
            else:
                raise ValueError(
                    "Either module_globals or module must be specified")
        self.path = path
        self.module = module
        resource = pkg_resources.resource_stream(module, path)

        data = resource.read()
        resource.close()
        content_type, enc=guess_content_type(path, data)
        if content_type:
            self.content_type=content_type
        else:
            self.content_type='image/%s' % path[path.rfind('.')+1:]
        self.__name__ = os.path.basename(path)
        if not is_zipped(module):
            try:
                self.lmt = os.path.getmtime(resource.name)
            except (OSError, AttributeError):
                self.lmt=time.time()
        else:
            self.lmt=time.time()
        self.lmh=rfc1123_date(self.lmt)

        if DevelopmentMode:
            # In development mode, a shorter time is handy
            max_age = 60 # One minute
        else:
            # A longer time reduces latency in production mode
            max_age = 3600 # One hour
        self.cch = 'public,max-age=%d' % max_age

    def read(self):
        return pkg_resources.resource_string(self.module, self.path)

    # If ImageFile had a read() method, we wouldn't need to override index_html
    def index_html(self, REQUEST, RESPONSE):
        """Default document"""
        # HTTP If-Modified-Since header handling. This is duplicated
        # from OFS.Image.Image - it really should be consolidated
        # somewhere...
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Last-Modified', self.lmh)
        RESPONSE.setHeader('Cache-Control', self.cch)
        header=REQUEST.get_header('If-Modified-Since', None)
        if header is not None:
            header=header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:    mod_since=long(DateTime(header).timeTime())
            except: mod_since=None
            if mod_since is not None:
                if getattr(self, 'lmt', None):
                    last_mod = long(self.lmt)
                else:
                    last_mod = long(0)
                if last_mod > 0 and last_mod <= mod_since:
                    RESPONSE.setStatus(304)
                    return ''

        return self.read()


class DTMLResource(DTMLFile):

    def __init__(self, path, module_globals=None, module=None, **kw):
        if module_globals is not None and module is not None:
            raise ValueError(
                "Cannot specify both module_globals and module")
        if module is None:
            if module_globals is not None:
                module = module_globals['__name__']
            else:
                raise ValueError(
                    "Either module_globals or module must be specified")
        #from DTMLFile.__init__(self, name, _prefix, **kw)
        self.ZBindings_edit(defaultBindings)
        self._setFuncSignature()

        #from ClassicHTMLFile.__init__(self, name, _prefix, **kw)
        path_with_ext = path + '.dtml'
        if not kw.has_key('__name__'):
            kw['__name__'] = os.path.basename(path)

        #from FileMixin.__init__(self, *args, **kw)
        self.raw = (module, path_with_ext)
        self.initvars(None, kw)
        self.setName(kw['__name__'])
        self.zipped = is_zipped(module)

    def read_raw(self):
        if self.edited_source:
            data = self.edited_source
        elif not self.raw:
            data = ''
        else:
            data = pkg_resources.resource_stream(*self.raw).read()
        return data
        
    def _cook_check(self):
        if DevelopmentMode and not self.zipped:
            __traceback_info__ = str(self.raw)
            package, path = self.raw
            f = pkg_resources.resource_stream(package, path)
            try:
                mtime = os.path.getmtime(f.name)
            except (OSError, AttributeError):
                mtime = 0
            if mtime != self._v_last_read:
                self.cook()
                self._v_last_read=mtime
        elif not hasattr(self,'_v_cooked'):
            try: changed = self.__changed__()
            except: changed=1
            self.cook()
            if not changed:
                self.__changed__(0)

def is_zipped(package_name):
    """Return true if the given named package is zipped, false if it is a
    plain old filesystem package
    """
    provider = pkg_resources.get_provider(package_name)
    return isinstance(provider, pkg_resources.ZipProvider)

