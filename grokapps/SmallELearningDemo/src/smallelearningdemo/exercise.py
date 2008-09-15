import grok
import app
import answercontainer
import filecontainer
import zope.interface
import zope.schema
import zope.component


class IExercise(zope.interface.Interface):

  name = zope.schema.ASCIILine(title=u'Name')

  title = zope.schema.TextLine(title=u'Title')

  description = zope.schema.Text(title=u'Description')


class Exercise(grok.Container):

  grok.implements(IExercise)

  def __init__(self, name, title, description):
    super(Exercise, self).__init__()
    self.name = name
    self.title = title
    self.description = description

    self['answers'] = answercontainer.AnswerContainer()
    self['files'] = filecontainer.FileContainer()


class Add(grok.AddForm):

  grok.context(app.SmallELearningDemo)

  form_fields = (grok.AutoFields(Exercise) +
                 grok.Fields(data=zope.schema.Bytes(title=u'Data',
                                                    default=None,
                                                    required=False))
                 )

  @grok.action('Add exercise')
  def add(self, name, title, description, data):
    exercise = Exercise(name=name, title=title, description=description)

    # Use add view defined in filecontainer.Add.
    addview = zope.component.getMultiAdapter((exercise['files'], self.request),
                                             name='add')
    addview.upload(data=data)

    self.context[exercise.name] = exercise
    self.redirect(self.url(exercise))


class Index(grok.View):

  def getFiles(self):
    return self.context['files'].values()


class Edit(grok.EditForm):

  form_fields = grok.AutoFields(Exercise).omit('name')

  @grok.action('Save')
  def save(self, **data):
    self.applyData(self.context, **data)
    self.redirect(self.url(self.context))


class Delete(grok.View):

  grok.context(app.SmallELearningDemo)

  def render(self):
    for name in self.request.form.get('names', ()):
      if name in self.context:
        del self.context[name]
    self.redirect(self.url(self.context))
