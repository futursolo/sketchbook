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
syntax. Actually, Sketchbook rewrites sketches into Python code and asks the
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

.. _raw-output:

Raw Output
----------
To output raw strings without escaping, use :code:`raw=` (or :code:`r=` for
shorthand) as a keyword. In this case, :code:`raw` is the escape function for
statement instead of :code:`default`.

For how to override the default escape function, define
custom escape functions and view built-in escape functions, please see the
documentation for :class:`.BaseSketchContext`.

Indentation
===========
Indentation is used to control the flow how the sketch is drawn. There're three
types of keywords to control the indentation:

- Indent keywords: :code:`if`, :code:`with`, :code:`for`, :code:`while`, :code:`try` and :code:`async`.
- Unident keyword: :code:`end`.
- Half-indent keywords: :code:`else`, :code:`elif`, :code:`except` and :code:`finally`.

Indent keywords is used to start an indentation, and the unindent keyword is used to
finish the indentation created by the last indent keyword.

Half Indentation
----------------
Half-indent keywords is a special type. It unindents the last indentation, and
establishes a new indentation at the same time.

Example:

.. code-block:: text

    <% if a == b %>
        <%= "They are the same." %>
    <% else %>
        <%= "They are not the same." %>
    <% end %>

The :code:`if` statement creates an indenation as discussed above, and the
:code:`else` statement will automatically unident the :code:`if` statement, and
establish an new indentation until another unindent statement or
half-indent statement is reached.

.. warning::

  Redundant unindent statements will raise a :class:`.SketchSyntaxError`.

Inline
======
The statement represents a Python inline keyword.

Example:

.. code-block:: text

    <% from time import time as get_timestamp %>
    <% import random %>

    <% while True %>
        <%r= str(get_timestamp()) %>
        <% if random.choice(range(0, 2)) %>
            <% break %>
        <% end %>
    <% end %>

This example will output time stamps until a positive value is selected by random function.

.. note::

    The keywords of inline statements are :code:`break`, :code:`continue`,
    :code:`import`, :code:`from`, :code:`raise`, :code:`assert`,
    :code:`nonlocal`, and :code:`global`.

Assignment
==========
In Python language, keyword :code:`=` is used to assign values to variables.
However, in order to set a variable in sketches, you have to use an additional
keyword :code:`let`:

.. code-block:: text

    <% try %>
        <%= a %>
    <% except NameError %>
        Variable a is not set.
    <% end %>

    <% let a = "whatever" %>
    Variable a is set to <%= a %>.

This should output

.. code-block:: text

    Variable a is not set.
    Variable a is set to whatever.

Include
=======
Include another sketch into the current sketch.

Example:

:code:`header.html`:

.. code-block:: text

    <header>
        <h1>Site Title</h1>
    </header>

:code:`main.html`:

.. code-block:: text

    <html>
        <head>
            <title>Main Page</title>
        </head>
        <body>
            <% include "header.html" %>
            <main>
                <p>Thank you for visiting.</p>
            </main>
        </body>
    </html>

When :code:`main.html` being drawn, it will ask the finder to find
:code:`header.html` and draw :code:`header.html` at the runtime,
then append it to the result of :code:`main.html`.

The result of the example above is:

.. code-block:: text

    <html>
        <head>
            <title>Main Page</title>
        </head>
        <body>
            <header>
                <h1>Site Title</h1>
            </header>
            <main>
                <p>Thank you for visiting.</p>
            </main>
        </body>
    </html>

Inheritance
===========
Inherit from other sketches. When a sketch with an :code:`inherit` statement is
being drawn, a subclass of :class:`.BaseSketchFinder` will find the parent sketch.
The parent sketch will then being drawn with :code:`.SketchRuntime.body` set to the output
of the original sketch. The blocks of the parent sketch will be replaced with the
ones in the child sketch.

Example:

:code:`layout.html`:

.. code-block:: text

    <html>
        <head>
            <title><% block title %><% end %></title>
            <% block head %><% end %>
        </head>
        <body>
            <%r= self.body %>
        </body>
    </html>

:code:`main.html`:

.. code-block:: text

    <% inherit "layout.html" %>
    <% block title %>Main Page<% end %>
    <main>
        <p>Thank you for visiting.</p>
    </main>

When :code:`main.html` being drawn, it will ask the sketch finder to find
:code:`layout.html` and update all the blocks in :code:`layout.html` with the blocks in
:code:`main.html`. The other content outside the blocks in :code:`main.html` can be
accessed using :code:`self.body` in :code:`layout.html`.

.. hint::

    If the inheritance is not enabled, the :code:`block` statement has no effect.

.. important::

    When drawing the :code:`self.body`, make sure to use :ref:`raw-output`,
    or the it may be escaped.

.. warning::

    If the sketch being drawn is not a parent of another sketch, using :code:`self.body`
    will raise an :class:`.SketchDrawingError`.

The result of the example above is:

.. code-block:: text

    <html>
        <head>
            <title>Main Page</title>
        </head>
        <body>
            <main>
        <p>Thank you for visiting.</p>
    </main>
        </body>
    </html>

Comment
=======
Strings that will be removed from the result.

.. code-block:: text

    This is the content.
    <%# This is the comment. %>

When the sketch is being drawn, the comment will be excluded.

The result of the example above is:

.. code-block:: text

    This is the content.
