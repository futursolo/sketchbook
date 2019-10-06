.. sketchbook documentation master file, created by
   sphinx-quickstart on Fri Apr 28 16:11:11 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _index:

====================
Sketchbook |release|
====================

.. code-block:: python3

    <% async for blank_page in sketchbook %>
        <% let sketch = await blank_page.draw() %>
    <% end %>

Sketchbook is a templating engine designed for asyncio. It takes advantage of
Python 3's unicode and :code:`async`/:code:`await` syntax(:pep:`492`)
written for :code:`asyncio` (:pep:`3156`) and `concurrent I/O <https://curio.readthedocs.io/>`_
with a syntax inspired by `ERB <https://en.wikipedia.org/wiki/ERuby>`_ and
`Django Templates <https://docs.djangoproject.com/en/stable/ref/templates/language/>`_.

Features
========
- Simple Syntax: The syntax of Sketchbook is easy to learn. It mixes
  the Python syntax with the ERB style tag marker.
- Safe: The output is escaped by default unless manually overridden.
- Unicode Support: Unicode is used by default. No need to worry about Python2
  bytestring.
- :code:`async`/:code:`await` ready: Sketchbook is designed
  to use with :code:`async`/:code:`await` syntax.
  Developer can use :code:`async`/:code:`await` syntax to the full extent.
- Fast Execution: Just like `Mako <http://www.makotemplates.org>`_ and
  `Jinja2 <http://jinja.pocoo.org>`_, Sketchbook compiles sketches
  into Python bytecode before execution, allowing it to be executed as fast as
  other Python code.
- Dynamic Template Inheritance and Inclusion: Sketches can inherit from and
  include the other sketches **at the runtime**, which significantly improve
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

Alternative Event Loop
======================
Beside the :code:`asyncio` module from the Python standard library, Sketchbook
can also be used with `curio <https://curio.readthedocs.io/en/latest/>`_.

Requirements
============
- Python 3.6.1+
- aiofiles>=0.3.1,<1(Optional, used by :class:`.AsyncSketchFinder`)

Usage
=====
-  :ref:`integration`.

- Language Reference:: :ref:`language`.

Why?
====
There are quite a few template engines for Python, why reinvent the wheel?

- Most template engines are relics from :code:`Python 2.x` hence they suck when dealing
  with unicode.
- Coroutine is now one of a first class feature in the Python language, but not in
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
