import grok
import zope.schema
import zope.file.file
import zope.file.upload
import zope.file.download


class FileContainer(grok.Container):

  pass


#### Example of using zope.app.file
## import zope.app.file
##
## class Add(grok.AddForm):
##   """An addview for zope.app.file"""
##   grok.context(FileContainer)
##
##   form_fields = grok.AutoFields(zope.app.file.interfaces.IFile).select('data')
##
##   @grok.action('Add file')
##   def add(self, **data):
##     self.upload(**data)
##     self.redirect(self.url(self.context.__parent__))
##
##   def upload(self, **data):
##     fileupload = self.request['form.data']
##     if fileupload and fileupload.filename:
##       contenttype = fileupload.headers.get('Content-Type')
##       file_ = zope.app.file.File(data['data'], contenttype)
##       self.context[fileupload.filename] = file_


class Add(grok.AddForm):
  """An addview for zope.file"""

  grok.context(FileContainer)

  form_fields = grok.Fields(
    zope.schema.Bytes(__name__='data',
                      title=u'Upload data',
                      description=u'Upload file',),
    )

  @grok.action('Add file')
  def addFile(self, data):
    self.upload(data)
    self.redirect(self.url(self.context.__parent__))

  def upload(self, data):
    fileupload = self.request['form.data']
    file_ = zope.file.file.File()
    zope.file.upload.updateBlob(file_, fileupload)
    self.context[fileupload.filename] = file_


class Index(grok.View):

  pass


class FileIndex(zope.file.download.Display, grok.View):
  """Default view for zope.file.file.File"""
  grok.name('index.html')
  grok.context(zope.file.file.File)

  def render(self):
    return self()
