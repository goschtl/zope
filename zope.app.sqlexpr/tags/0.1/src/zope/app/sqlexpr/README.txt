SQL TALES Expression

  The goal of the SQL TALES expression is to allow quick SQL queries
  right out of TALES expressions and Zope Page Templates. While this
  is certainly not the Zopeish way of doing things, it allows the
  newbie Web scripter an easier entrance to the world of Zope 3.

  SQL Expressions behave very similar to String Expressions, but
  before they return, they are making an SQL call to the database and
  return a ResultSet.

  Example 1 - Once you have setup a SQL Connection, you can just use
  this connection by setting the variable 'sql_conn'. From then on
  this connection is used to execute the SQL statements::

    <html tal:define="sql_conn string:psycopg_test">
      <body>
         <ul>
            <li tal:repeat="contact sql: SELECT * FROM contact">
               <b tal:content="contact/name" />
            </li>
         </ul>
      </body>
    </html>

  Example 2 - In case you do not want to deal with any Component
  Architecture details at all, then you can simply specify the
  connection type and the DSN and the connection is created for you at
  runtime::

    <html tal:define="rdb string:PsycopgDA; dsn string:dbi://test">
      <body>
         <ul>
            <li tal:repeat="contact sql: SELECT * FROM contact">
               <b tal:content="contact/name" />
            </li>
         </ul>
      </body>
    </html>

  Example 3 - throwing in some variables to make it interesting::

    <html tal:define="rdb string:PsycopgDA; dsn string:dbi://test">
      <body>
         <ul tal:define="name string:Stephan; table string:contact">
            <li tal:repeat="
                contact sql: SELECT * FROM ${table} WHERE name = '${name}'">
              <b tal:content="contact/name" />
            </li>
         </ul>
      </body>
    </html>


  Installation

    Add the following line to products.zcml file::

      <include package="zope.app.sqlexpr" />

    However, the product is useless unless you install a relational
    database adapter or get a Gadfly database setup (the DA for Gadfly
    comes with Zope 3).
