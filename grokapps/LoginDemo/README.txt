LoginDemo is a sample application showing how to implement user account
creation and login using Grok. 

Main features
-------------

- top bar displays user data and login status

- links in top bar change according to login status

- user can create own account

- a list of created accounts can be seen in the member listing page

- member listing page is protected by permission, requiring user log in

- member e-mail is stored as an annotation

- good functional test coverage (see text files in src/logindemo/ftests)

Todo
----

- allow user to edit his data (password, real name, e-mail)

- password reset for users with a valid e-mail

- allow manager to delete user accounts through the member listing

- find out the best way to embed auto-generated forms in our master template

