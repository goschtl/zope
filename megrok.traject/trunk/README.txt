megrok.traject
**************

``megrok.traject`` is a library that integrates the traject_ routing
framework with the Grok_ web framework.

.. _traject: http://pypi.python.org/pypi/traject

.. _grok: http://grok.zope.org

Include ``megrok.traject`` by adding it in your Grok project's
``setup.py`` (in ``install_requires``) and re-run buildout.

External trajects
-----------------

External trajects are most useful if you do not directly control the
models. This may for instance be the case if the models are defined in
an external package.

With ``megrok.traject`` you can declare trajects in Grok like this::

  from megrok import traject

  class SomeTraject(traject.Traject):
      grok.context(App)
     
      pattern = 'departments/:department_id'
      model = Department

      def factory(department_id):
          return get_department(department_id)

      def arguments(department):
          return dict(department_id=department.id)

This registers ``factory`` and the inverse ``arguments`` functions for
the pattern ``departments/:department_id``, the root ``App`` and the
class ``Department``. This replaces the ``register*`` functions in
traject itself.

``App`` is any grok model. This model now automatically allows
traversal into the associated patterns; the system registers a custom
traverser to do this.

You can register grok views for ``Department`` as usual.

Context issues
--------------

If you *can*, make the models exposed by traject subclass from
``grokcore.component.Context`` (or its alias ``grok.Context``, or its
alias ``traject.Context``). By doing so, you avoid the problems
described below. 

Sometimes you cannot subclass your models from
``grokcore.component.Context``, however. Exposing external models was
something that megrok.traject was designed to allow, after all.

When you use megrok.traject with external models, you can run into the
following two issues with your models:

* The ZTK assumes the default view for objects is ``index.html``, not
  ``index``. The ``index`` default view setting is only used when you
  subclass your model from ``grokcore.component.Context``. You can
  still make ``index`` the default view of your model by adding the
  following directive to your project's ``configure.zcml``::

     <browser:defaultView
       for="SomeForeignModel"
       name="index"
       />

  You can also do this for a common base class that you know all your
  models share, or a common interface that you know is provided by all
  your models.

* Views, adapters and such won't auto-associate with your models in
  the same module. You will need to explicitly use the
  ``grok.context()`` on the module or class level to associate your
  component. For example::

    class SomeForeignModel(object):
        ...

    class MyView(grok.View):
        grok.context(SomeForeignModel)

Traject models
--------------

If you have control over the model definitions yourself, traject
allows a more compact notation that lets you define traject-based
models directly::

  import traject

  class Department(traject.Model):   
    traject.context(App) 
    traject.pattern('departments/:department_id')

    def factory(department_id):
        return get_department(department_id)
    
    def arguments(self):
        return dict(department_id=self.id)

``traject.Model`` derives from ``grokcore.component.Context``, so the
issues mentioned above with external models won't be a problem here.

Note that Traject models are not persistent in the ZODB sense. If you
need a persistent Traject models you can mix in ``grok.Model`` or
``persistent.Persistent``.

Tips
----

* return ``None`` in factory if the model cannot be found. The system
  then falls back to normal traversal to look up the view. Being too
  aggressive in consuming any arguments will break view traversal.

* Use ``megrok.traject.locate`` to locate an object before asking for
  its URL or doing ``checkPermission`` on it. If the object was routed
  to using ``megrok.traject`` already this isn't necessary. This is
  a simple import alias for ``traject.locate``.

* Instead of normal methods (which get interpreted as functions) for
  ``factory`` and ``arguments``, you can also turn them into class
  methods using the ``@@classmethod`` decorator. They now take a
  ``cls`` argument as the first argument which is the class they are
  defined on. This can be useful if you want to make the
  implementations of these functions depend on information on its
  class (such as the value of ``model``), and this in turn can be
  useful to implement more declarative traject base classes.

For more information see the traject_ documentation.

.. _traject: http://pypi.python.org/pypi/traject

