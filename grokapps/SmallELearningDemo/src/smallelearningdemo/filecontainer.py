import grok
import zope.app.file


class FileContainer(grok.Container):

  pass


class Add(grok.AddForm):

  grok.context(FileContainer)

  form_fields = grok.AutoFields(zope.app.file.interfaces.IFile).select('data')

  @grok.action('Add file')
  def add(self, **data):
    self.upload(**data)
    self.redirect(self.url(self.context.__parent__))

  def upload(self, **data):
    fileupload = self.request['form.data']
    if fileupload and fileupload.filename:
      contenttype = fileupload.headers.get('Content-Type')
      file_ = zope.app.file.File(data['data'], contenttype)
      self.context[fileupload.filename] = file_


class Index(grok.View):

  pass
