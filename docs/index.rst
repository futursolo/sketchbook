.. sketchbook documentation master file, created by
   sphinx-quickstart on Fri Apr 28 16:11:11 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _index:

====================
Sketchbook |version|
====================

.. code-block:: python3

    <% async for blank_page in sketchbook %>
        <% let sketch = await blank_page.draw() %>
    <% end %>

Sketchbook is a brand new template engine for asyncio. It takes advantage of
Python 3's unicode, :code:`asyncio` (:pep:`3156`) and
the new :code:`async`/:code:`await` syntax(:pep:`492`),
with a syntax inspired by `ERB <https://en.wikipedia.org/wiki/ERuby>`_ and
`Django Templates <https://docs.djangoproject.com/en/stable/ref/templates/language/>`_.

Features
========
- Super Simple Syntax: The syntax of Sketchbook is super easy to learn. It mixes
  the Python syntax with the ERB style tag marker while keeping a big picture from Python.
- Safe: The output is escaped by default unless manually overridden.
- Unicode Support: Unicode is baked into the whole system, never worry about dealing with
  the bytestring.
- Fully :code:`asyncio` and :code:`async`/:code:`await` ready: Sketchbook is designed
  from the ground up for :code:`asyncio` module and :code:`async`/:code:`await` syntax.
  Developers are able to use :code:`async for`, :code:`async with` and :code:`await`
  fearlessly.
- Fast Execution: Like `Mako <http://www.makotemplates.org>`_ and
  `Jinja2 <http://jinja.pocoo.org>`_, Sketchbook compiles the template
  into Python bytecode before execution, it should be as fast as running other
  Python code.
- Dynamic Template Inheritance and Including: The template can inherit from and
  include the other templates **at the runtime**, which significantly improves
  the reusability and flexibility.

Intallation
===========
.. code-block:: shell

    $ pip install -U sketchbook

Source Code
===========
:code:`sketchbook` is open sourced under
`Apache License 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_ and its
source code is hosted on `GitHub <https://github.com/futursolo/sketchbook/>`_.

Requirements
============
- Python 3.6+
- aiofiles>=0.3.1,<1(For :class:`.SketchFinder`)

Usage
=====
- For how to integrate sketchbook into your project, see :ref:`integration`.

- For the Language Reference , please refer to :ref:`language`.

Why?
====
There's quite a few template engines for Python, why reinvent the wheel?

- Most template engines are relics from :code:`Python 2.x`, thus they suck when dealing
  with unicode.
- The coroutine is now one of the first class citizens in the Python language, but not in
  these template engines.
- None of them support the new type hints system introduced in :code:`Python 3.5`.
- It's fun!

See also
========
.. toctree::
   :maxdepth: 3

   integration
   language
   sketchbook

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
