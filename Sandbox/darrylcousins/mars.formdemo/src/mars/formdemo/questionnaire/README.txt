==================
Questionnaire Demo
==================

The purpose of the questionnaire demo is demonstrate the concept of field
groups and attribute value adapters for fields.

To start, we need to open a browser and go to the demo applications overview
screen:

  >>> from z3c.formdemo import testing
  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.handleErrors = False
  >>> user.addHeader('Accept-Language', 'en')
  >>> skinURL = 'http://localhost:8080/++skin++marsformdemo'
  >>> user.open('http://localhost:8080')

Since all demos are purely public, there is no need to log in. Let's now click
on the "All widgets" link:

  >>> user.open(skinURL + '/questionnaireResults')

The first screen you see is the questionnaire results screen.

  >>> testing.printElement(user, "//h1")
  <h1>Zope Developer Questionnaire Results</h1>

Initially there are no questionnaires, so the screen contains little
information. Let's first fill out a questionnaire by click on the link below
the table.

  >>> user.getLink('Fill out Questionnaire').click()

The user is now presented with the questionnaire screen, which is organized
into three groups. Let's fill out the questionnaire:

  >>> user.getControl('Name').value = u'Stephan Richter'
  >>> user.getControl('Age').value = u'27'

  >>> user.getControl('yes', index=0).click()
  >>> user.getControl('no', index=1).click()
  >>> user.getControl('yes', index=2).click()
  >>> user.getControl('no', index=3).click()

  >>> user.getControl('yes', index=4).click()
  >>> user.getControl('have you contributed').value = u'5'
  >>> user.getControl('What is your Zope Id?').value = u'srichter'

  >>> user.getControl('Submit Questionnaire').click()

Once the questionnaire has been submitted, the user is returned to the results
screen. Now the table has an entry:

  >>> testing.printElement(user, "//table/tbody/tr[1]")
  <tr class="odd"><td
     class="sorted-on">
      Stephan Richter
    </td>
    <td class="right">
      27
    </td>
    <td class="right">
      yes
    </td>
    <td class="right">
      no
    </td>
    <td class="right">
      yes
    </td>
    <td class="right">
      no
    </td>
    <td class="right">
      yes
    </td>
    <td class="right">
      5
    </td>
    <td class="right">
      srichter
    </td>
  </tr>

Let's now fill out another questionnaire:

  >>> user.getLink('Fill out Questionnaire').click()

  >>> user.getControl('Name').value = u'Roger Ineichen'
  >>> user.getControl('Age').value = u'39'

  >>> user.getControl('yes', index=0).click()
  >>> user.getControl('yes', index=1).click()
  >>> user.getControl('yes', index=2).click()
  >>> user.getControl('no', index=3).click()

  >>> user.getControl('yes', index=4).click()
  >>> user.getControl('have you contributed').value = u'4'
  >>> user.getControl('What is your Zope Id?').value = u'projekt01'

  >>> user.getControl('Submit Questionnaire').click()

Now that we have two entries, we can use the table headers cells to sort
them. By default they are sorted by name:

  >>> testing.printElement(user, "//table/tbody/tr/td[1]/text()",
  ...                      multiple=True, serialize=False)
  Roger Ineichen
  Stephan Richter

Clicking on the "Name" table header cell, will leave the order, since the
ordering must be initialized. The second time the order is reversed:

  >>> user.getLink('Name').click()
  >>> user.getLink('Name').click()

  >>> testing.printElement(user, "//table/tbody/tr/td[1]/text()",
  ...                      multiple=True, serialize=False)
  Stephan Richter
  Roger Ineichen

Selecting another header will sort on it. Let's choose the age; clicking on it
once sorts it in ascending order:

  >>> user.getLink('Age').click()
  >>> testing.printElement(user, "//table/tbody/tr/td[2]/text()",
  ...                      multiple=True, serialize=False)
  27
  39

Clicking it again, reverses the order:

  >>> user.getLink('Age').click()
  >>> testing.printElement(user, "//table/tbody/tr/td[2]/text()",
  ...                      multiple=True, serialize=False)
  39
  27

Finally, let's make sure that all headers are linked:

  >>> user.getLink('Zope 2')
  <Link text='Zope 2' url='...?sort-on=formdemo.questionnaire.zope2'>
  >>> user.getLink('Plone')
  <Link text='Plone' url='...?sort-on=formdemo.questionnaire.plone'>
  >>> user.getLink('Zope 3')
  <Link text='Zope 3' url='...?sort-on=formdemo.questionnaire.zope3'>
  >>> user.getLink('Five')
  <Link text='Five' url='...?sort-on=formdemo.questionnaire.five'>
  >>> user.getLink('Contrib.')
  <Link text='Contrib.' url='...?sort-on=formdemo.questionnaire.contributor'>
  >>> user.getLink('Years')
  <Link text='Years' url='...?sort-on=formdemo.questionnaire.years'>
  >>> user.getLink('Zope Id')
  <Link text='Zope Id' url='...?sort-on=formdemo.questionnaire.zopeId'>
