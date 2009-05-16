
import re
import os
from datetime import datetime
import grok
import time
import uuid
import tempfile
import base64
import zipfile
import glob
import shutil
from zope import interface, schema
from zopyx.convert2.convert import Converter

default_tempdir = unicode(tempfile.tempdir)

class ManageServer(grok.Permission):
    grok.name('zopyx.smartprintng.server.manage')

class IServer(interface.Interface):
    title = schema.TextLine(title=u'Title of this instance', 
                            required=True)
    spool_directory = schema.TextLine(title=u'Spool directory', 
                                      default=default_tempdir,
                                      required=True)


class Zopyx_smartprintng_server(grok.Application, grok.Container):
    """ This is the base of all evil """    

    interface.implements(IServer)

    title = u''
    spool_directory = default_tempdir

    def addJob(self, *args, **kw):
        if not 'accounting' in self:
            self['accounting'] = Accounting()
        self['accounting'].addJob(*args, **kw)
        self._p_changed = 1


class EditForm(grok.EditForm):
    """ Eggserver's edit form """

    grok.name('edit')
    grok.require('zopyx.smartprintng.server.manage')
    grok.context(IServer)
    form_fields = grok.AutoFields(IServer)

    @grok.action('Apply changes')
    def applyChanges(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context))

    @grok.action('Cancel')
    def returnToIndex(self, **data):
        self.redirect(self.url(self.context))


class Accounting(grok.Container):
    """ A folder for Job objects """

    num_items = 0

    def addJob(self, *args, **kw):
        self.num_items += 1
        self[str(self.num_items)] = Job(*args, **kw)
        self._p_changed = 1


class Job(grok.Model):
    """ Holds informations about each conversion job """

    def __init__(self, *args, **kw):
        super(Job, self).__init__()
        self.created = datetime.now()
        for k,v in kw.items():
            setattr(self, k, v)

class Index(grok.View):
    grok.context(Zopyx_smartprintng_server)

class ShowJobs(grok.View):
    grok.context(Zopyx_smartprintng_server)

    def getJobs(self):
        lst = list(self.context['accounting'].values())
        lst.sort(lambda x,y: -cmp(x.created, y.created))
        return lst

class Master(grok.View):
    grok.context(Zopyx_smartprintng_server)

class Download(grok.View):
    """ Provides download functionality for generated files over HTTP"""

    grok.context(Zopyx_smartprintng_server)

    def render(self, id, extension='pdf'):
        """ Return generated PDF file """

        filename = os.path.join(self.context.spool_directory, 
                                '%s.%s' % (id, extension))
        r = self.response
        if not os.path.exists(filename):
            r.setStatus(404)
            return

        r.setHeader('content-type', 'application/pdf')
        r.setHeader('content-disposition', 'attachment; filename="%s"' % 
                     toAscii(os.path.basename(filename)))
        return file(filename)


#######################################
# The XML-RPC API
#######################################

class XMLRPC(grok.XMLRPC):

    grok.context(Zopyx_smartprintng_server)

    rxcountpages = re.compile(r"$\s*/Type\s*/Page[/\s]", re.MULTILINE|re.DOTALL)

    def _countPages(self, filename):
        data = file(filename,"rb").read()
        return len(self.rxcountpages.findall(data))

    def convertZIP(self, zip_archive, spool=0, converter_name='pdf-prince'):
        """ Process html-file + images within a ZIP archive """

        # store zip archive first
        tempdir = tempfile.mkdtemp()
        zip_temp = os.path.join(tempdir, 'input.zip')
        file(zip_temp, 'wb').write(base64.decodestring(zip_archive))
        ZF = zipfile.ZipFile(zip_temp, 'r')
        for name in ZF.namelist():
            destfile = os.path.join(tempdir, name)
            if not os.path.exists(os.path.dirname(destfile)):
                os.makedirs(os.path.dirname(destfile))
            file(destfile, 'wb').write(ZF.read(name))
        ZF.close()

        # find HTML file
        html_files = glob.glob(os.path.join(tempdir, '*.htm*'))
        if not html_files:
            raise IOError('No HTML files found in %s' % tempdir)
        html_filename = html_files[0]

        result = self.convert(html_filename, 
                              spool=spool, 
                              converter_name=converter_name)

        # Generate result ZIP archive with base64-encoded result
        zip_out = os.path.join(tempdir, 'output.zip')
        ZF = zipfile.ZipFile(zip_out, 'w')
        ZF.writestr('output.pdf', file(result, 'rb').read())
        ZF.close()
        encoded_result = base64.encodestring(file(zip_out, 'rb').read())
        shutil.rmtree(tempdir)
        return encoded_result

    def convert(self, html_filename, spool=0, converter_name='pdf-prince'):
        """ Process a single HTML file """

        start_time = time.time()
        c = Converter(html_filename)
        output_filename = c(converter_name)
        file_size = os.stat(output_filename)[6]
        duration = time.time() - start_time
        self.context.addJob(input_filename=html_filename, 
                            output_filename=output_filename,
                            output_size=file_size,
                            duration=duration,
                            pages=self._countPages(output_filename),
                            converter_name=converter_name)
        if spool:
            id = uuid.uuid1()
            if not os.path.exists(self.context.spool_directory):
                os.makedirs(self.context.spool_directory)
            new_filename = os.path.join(self.context.spool_directory, 
                                        '%s.pdf' % id)
            os.rename(output_filename, new_filename)
            return grok.url(self.request, self.context) + \
                            '/download?id=%s' % id
        else:
            return output_filename

def _c(s):
    if isinstance(s, unicode):
        return s
    try:
        return unicode(s, 'utf-8')
    except UnicodeError:
        return unicode(s, 'iso-8859-15')

def toAscii(s):
    return _c(s).encode('ascii', 'ignore')


class BaseForm(grok.AddForm):
    grok.context(Zopyx_smartprintng_server)

    def _deliver(self, filename):
        """ Return generated PDF file """
        r = self.response
        r.setHeader('content-type', 'application/pdf')
        r.setHeader('content-length', os.stat(filename)[6])
        r.setHeader('content-disposition', 'attachment; filename="%s"' % 
                     toAscii(os.path.basename(filename)))
        return file(filename)

