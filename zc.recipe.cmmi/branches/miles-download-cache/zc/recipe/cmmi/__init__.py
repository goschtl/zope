##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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

import logging, os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util
import datetime
import sha
import zc.buildout

def system(c):
    if os.system(c):
        raise SystemError("Failed", c)

class Recipe:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        directory = buildout['buildout']['directory']
        self.download_cache = buildout['buildout'].get('download-cache')
        self.install_from_cache = buildout['buildout'].get('install-from-cache')

        url = self.options['url']
        _, _, urlpath, _, _, _ = urlparse.urlparse(url)
        self.filename = urlpath.split('/')[-1]
        if self.download_cache:
            # cache keys are hashes of url, to ensure repeatability if the
            # downloads do not have a version number in the filename
            # cache key is a directory which contains the downloaded file
            # download details stored with each key as cache.ini
            cache_fname = sha.new(url).hexdigest()
            self.download_cache = os.path.join(directory, self.download_cache, 'cmmi')
            self.cache_name = os.path.join(self.download_cache, cache_fname)

        # we assume that install_from_cache and download_cache values
        # are correctly set, and that the download_cache directory has
        # been created: this is done by the main zc.buildout anyway
          
        if not options.has_key('location'):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                name)
        options['prefix'] = options['location']

    def install(self):
        dest = self.options['location']
        url = self.options['url']
        extra_options = self.options.get('extra_options', '')
        # get rid of any newlines that may be in the options so they
        # do not get passed through to the commandline
        extra_options = ' '.join(extra_options.split())
        patch = self.options.get('patch', '')
        patch_options = self.options.get('patch_options', '-p0')

        if self.download_cache:
            if not os.path.isdir(self.download_cache):
                os.mkdir(self.download_cache)

        # get the file from the right place
        fname, tmp2 = None, None
        if self.download_cache:
            # if we have a cache, try and use it
            logging.getLogger(self.name).debug(
                'Searching cache at %s' % self.download_cache )
            if os.path.isdir(self.cache_name):
                # just cache files for now
                fname = os.path.join(self.cache_name, self.filename)
                logging.getLogger(self.name).debug(
                    'Using cache file %s' % self.cache_name )

            else:
                logging.getLogger(self.name).debug(
                    'Did not find %s under cache key %s' % (self.filename, self.cache_name) )

        if not fname:
            if self.install_from_cache:
                # no file in the cache, but we are staying offline
                raise zc.buildout.UserError(
                    "Offline mode: file from %s not found in the cache at %s" % 
                    (url, self.download_cache) )

            try:
                # okay, we've got to download now
                # XXX: do we need to do something about permissions
                # XXX: in case the cache is shared across users?
                tmp2 = None
                if self.download_cache:
                    # set up the cache and download into it
                    os.mkdir(self.cache_name)
                    fname = os.path.join(self.cache_name, self.filename)
                    if self.filename != "cache.ini":
                        now = datetime.datetime.utcnow()
                        cache_ini = open(os.path.join(self.cache_name, "cache.ini"), "w")
                        print >>cache_ini, "[cache]"
                        print >>cache_ini, "download_url =", url
                        print >>cache_ini, "retrieved =", now.isoformat() + "Z"
                        cache_ini.close()
                    logging.getLogger(self.name).debug(
                        'Cache download %s as %s' % (url, self.cache_name) )
                else:
                    # use tempfile
                    tmp2 = tempfile.mkdtemp('buildout-'+self.name)
                    fname = os.path.join(tmp2, self.filename)
                    logging.getLogger(self.name).info(
                        'Downloading %s' % url )
                open(fname, 'w').write(urllib2.urlopen(url).read())
            except:
                if tmp2 is not None:
                   shutil.rmtree(tmp2)
                if self.download_cache:
                   shutil.rmtree(self.cache_name)
                raise

        try:
            # now unpack and work as normal
            tmp = tempfile.mkdtemp('buildout-'+self.name)
            logging.getLogger(self.name).info( 'Unpacking and configuring %s' % self.filename)
            setuptools.archive_util.unpack_archive(fname, tmp)
            
            os.mkdir(dest)
            here = os.getcwd()
            try:
                os.chdir(tmp)                                        
                try:
                    if not os.path.exists('configure'):
                        entries = os.listdir(tmp)
                        if len(entries) == 1:
                            os.chdir(entries[0])
                        else:
                            raise ValueError("Couldn't find configure")
                    if patch is not '':
                        system("patch %s < %s" % (patch_options, patch))
                    system("./configure --prefix=%s %s" %
                           (dest, extra_options))
                    system("make")
                    system("make install")
                finally:
                    os.chdir(here)
            except:
                os.rmdir(dest)
                raise

        finally:
            shutil.rmtree(tmp)
            if tmp2 is not None:
               shutil.rmtree(tmp2)

        return dest

    def update(self):
        pass
 
