megrok.traject
**************

``megrok.traject`` is a library that integrates the traject_ routing
framework with the Grok_ web framework.

.. _traject: http://pypi.python.org/pypi/traject

.. _grok: http://grok.zope.org

Include ``megrok.traject`` by adding it in your Grok project's
``setup.py`` (in ``install_requires``) and re-running buildout.

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

Tips:

* return ``None`` in factory if the model cannot be found. The system
  then falls back to normal traversal to look up the view. Being too
  aggressive in consuming any arguments will break view traversal.

* Use ``megrok.traject.locate`` to locate an object before asking for
  its URL or doing ``checkPermission`` on it. If the object was routed
  to using ``megrok.traject`` already this isn't necessary. This is
  a simple import alias for ``traject.locate``.

For more information see the traject_ documentation.

.. _traject: http://pypi.python.org/pypi/traject

