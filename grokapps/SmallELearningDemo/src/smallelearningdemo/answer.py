import grok
import answercontainer
import filecontainer
import zope.interface
import zope.schema
import zope.schema
import zope.component


class IAnswer(zope.interface.Interface):

  name = zope.schema.ASCIILine(title=u'Name')

  title = zope.schema.TextLine(title=u'Title')

  comment = zope.schema.Text(title=u'Comment')


class Answer(grok.Container):

  grok.implements(IAnswer)

  def __init__(self, name, title, comment):
    super(Answer, self).__init__()

    self.name = name
    self.title = title
    self.comment = comment

    self['files'] = filecontainer.FileContainer()


class Add(grok.AddForm):

  grok.context(answercontainer.AnswerContainer)

  form_fields = (grok.AutoFields(Answer) +
                 grok.Fields(data=zope.schema.Bytes(title=u'Data',
                                                    default=None,
                                                    required=False))
                 )

  @grok.action('Add answer')
  def add(self, name, title, comment, data):
    answer = Answer(name=name, title=title, comment=comment)

    # Use add view defined in filecontainer.Add.
    addview = zope.component.getMultiAdapter((answer['files'], self.request),
                                             name='add')
    addview.upload(data=data)

    self.context[answer.name] = answer
    self.redirect(self.url(answer))


class Index(grok.View):

  def getFiles(self):
    return self.context['files'].values()


class Edit(grok.EditForm):

  form_fields = grok.AutoFields(Answer).omit('name')

  @grok.action('Save')
  def save(self, **data):
    self.applyData(self.context, **data)
    self.redirect(self.url(self.context))
