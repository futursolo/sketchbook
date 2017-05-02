.. _language:

==============================
The Sketch Templating Language
==============================
The sketch templating language is aiming to generate flexible output for arbitrary
text file. It is designed for Pythonistas with statement marks inspired by ERB
and a Python like grammar. You should feel familiar with Sketch if you are
familiar with Python.

Example
=======
.. code-block:: text

    <!DOCTYPE>
    <html>
        <head>
            <title><%= await handler.get_page_title() %></title>
        </head>
        <body>
            <main>
                <% async for item in handler.db.items.find() %>
                    <article>
                        <div class="title"><%= item["title"] %></div>
                        <div class="author"><%= item["author"] %></div>
                        <div class="content"><%= item["content"] %></div>
                    </article>
                <% end %>
            </main>
        </body>
    </html>

The contents between :code:`<%` and :code:`%>` look quite similar to the Python
syntax. Actually, Sketchbook rewrites the sketch into Python code and asks the
Python interpreter to "compile" the plain Python code into Python byte code.

Hence, You can use (almost) any Python syntax in your sketches but with some
modifications:

1. All the python style syntax is wrapped between :code:`<%` and :code:`%>`.
2. Indent Is not indicated by :code:`:` any more, but controlled by a special
   :code:`<% end %>` statement.

Also, :func:`print` function still prints to :code:`sys.stdout` by default.
To print to the template, use :meth:`.SketchRuntime.write` or output
statements.

Statement Mark
==============
All the statements of sketches are wrapped under statement marks -
:code:`<%` and :code:`%>`.

Statement Mark Escape
---------------------
:code:`<%%` and :code:`%%>` escape :code:`<%` and :code:`%>` respectively.
e.g.: The following sketch::

    <%% is the begin mark, and <%r= "%%> is the end mark. " %>
    <%r= "<% and" %> %> only need to be escaped whenever they
    have ambiguity of the templating system.

will be drawn like::

    <% is the begin mark, and %> is the end mark.
    <% and %> only need to be escaped whenever they
    have ambiguity of the templating system.

Output
======
The simplest and the most common-used(perhaps) statement in the whole
Templating System.

.. code-block: python3
    Hello, <%= user.name %>.

:code:`=` is the statement keyword, and the expression following the keyword
will be evaluated by the interpreter. You can also :code:`await` an
:class:`collections.abc.Awaitable`::

    Hello, <%= await user.get_user_name() %>.

The result will be passed to :meth:`.SketchRuntime.write()` and escaped by the
default escape function.

Raw Output
----------
To output raw strings without escaping, use :code:`raw=` (or :code:`r=` for
shorthand) as a keyword. In this case, :code:`raw` is the escape function for
statement instead of :code:`default`.

For how to override the default escape function, define
custom escape functions and view built-in escape functions, please see the
documentation for :class:`.SketchContext`.

