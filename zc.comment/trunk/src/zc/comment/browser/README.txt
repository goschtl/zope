=============
Commenting UI
=============

Create the browser object we'll be using.

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Accept-Language', 'test')

To see how comments work, we'll create an instance of a simple content
object:

    >>> browser.open('http://localhost/@@contents.html')
    >>> browser.getLink('[[zope][[top]]]').click()
    >>> browser.getLink('[[zc.comment][Content]]').click()
    >>> browser.getControl(name='new_value').value = 'number'
    >>> browser.getControl('[[zope][container-apply-button (Apply)]]').click()

Let's visit the object and click on the comments tab:

    >>> browser.handleErrors = False
    >>> browser.getLink('number').click()
    >>> browser.getLink('[[zc.comment][Comments]]').click()

We see that no comments have been made yet:

    >>> '[[zc.intranet][No comments have been made.]]' in browser.contents
    True

Let's add a new multi-line comment:

    >>> browser.getControl('[[zc.comment][New Comment]]').value = '''\
    ... I give my pledge, as an Earthling
    ... to save, and faithfully defend from waste
    ... the natural resources of my planet.
    ... It's soils, minerals, forests, waters, and wildlife.
    ... '''

    >>> browser.getControl('[[zc.comment][Add Comment]]').click()

Now, we get a table that displays the comment with it's date, text,
and the user who made it:

    >>> print browser.contents
    <...
          <th>
          ...[[zc.comment][comment_column-date (Date)]]...
          </th>
          <th>
          ...[[zc.comment][comment_column-principals (Principals)]]...
          </th>
          <th>
            [[zc.comment][comment_column-comment (Comment)]]
          </th>
        ...
        <td>
          2005 11 14  12:00:55 -500
        </td>
        <td>
          Unauthenticated User
        </td>
        <td>
          I give my pledge, as an Earthling<br />
    to save, and faithfully defend from waste<br />
    the natural resources of my planet.<br />
    It's soils, minerals, forests, waters, and wildlife.<br />
    ...
     <label for="form.comment">
        <span class="required">*</span><span>[[zc.comment][New Comment]]</span>
      </label>
      ...<textarea class="zc-comment-text"
                   style="width: 50ex; height: 6em;"
                   cols="60" id="form.comment"
                   name="form.comment" rows="15" ></textarea></div>
    ...
        <input type="submit"
               id="form.actions.41646420436f6d6d656e74"
               name="form.actions.41646420436f6d6d656e74"
               value="[[zc.comment][Add Comment]]"
               class="button" />
    ...

Now, we'll add another comment.

    >>> browser.getControl('[[zc.comment][New Comment]]'
    ...     ).value = 'another comment'
    >>> browser.getControl('[[zc.comment][Add Comment]]').click()
    >>> print browser.contents
    <...
          <th>
    ...[[zc.comment][comment_column-date (Date)]]...
          </th>
          <th>
    ...[[zc.comment][comment_column-principals (Principals)]]...
          </th>
          <th>
            [[zc.comment][comment_column-comment (Comment)]]
          </th>
      </tr>
    ...
        <td>
          2005 11 14  12:10:18 -500
        </td>
        <td>
          Unauthenticated User
        </td>
        <td>
          I give my pledge, as an Earthling<br />
    to save, and faithfully defend from waste<br />
    the natural resources of my planet.<br />
    It's soils, minerals, forests, waters, and wildlife.<br />
    <BLANKLINE>
        </td>
      </tr>
      ...
        <td>
          2005 11 14  12:10:18 -500
        </td>
        <td>
          Unauthenticated User
        </td>
        <td>
          another comment
        </td>
      </tr>
    ...
    <label for="form.comment">
      <span class="required">*</span><span>[[zc.comment][New Comment]]</span>
    </label>
    ...
    ...<textarea class="zc-comment-text"
                 style="width: 50ex; height: 6em;"
                 cols="60"
                 id="form.comment"
                 name="form.comment"
                 rows="15" ></textarea>...
        <input type="submit"
               id="form.actions.41646420436f6d6d656e74"
               name="form.actions.41646420436f6d6d656e74"
               value="[[zc.comment][Add Comment]]"
               class="button" />
    ...
