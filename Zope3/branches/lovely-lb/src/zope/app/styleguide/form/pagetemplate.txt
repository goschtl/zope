=============
Page template
=============

Associate labels explicitly with their controls
-----------------------------------------------

In other words it means: use <label> along with your <input type="text"/>,
your <input type="checkbox"/> and your <input type="radio"/> elements.
Using labels makes it possible to use the pointer on the label
(clicking on the label) to active the input, so that it is easier to select a
text input, a check box or a radio box, just like it is in heavy client
applications such as Firefox.

Example::

  <label for="firstName">First name:
    <input type="text" name="firstname" id="firstName"/>
  </label>

cf. "Labeling form controls"
http://www.w3.org/TR/WCAG10-HTML-TECHS/#forms-labels

Element ID
----------

Use the "id" attribute to provide relative location URL instead of the old 
<a name="xxx"/> markup. This is needed to do the transition to XHTML1.1.

Example::

    <p>
      Check the <a href="#subject">subject headings</a>.
    </p>

    <h3 id="subject">Subject</h3>
    <p>
      Blah blah.
    </p>

Structure your text into paragraphs using <p>.
----------------------------------------------
To create paragraphs do not use <br/><br/>.

Example::

  <p>
    Blablah
  </p>
  <p>
    Blablah
  </p>
  <p>
    <input type="checkbox" name="item1" id="item1" value="xxx"/><label for="item1">Item1</label><br/>
    <input type="checkbox" name="item2" id="item2" value="yyy"/><label for="item2">Item2</label><br/>
    <input type="checkbox" name="item3" id="item3" value="zzz"/><label for="item3">Item3</label><br/>
  </p>
