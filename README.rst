Sketchbook
==========
.. image:: https://github.com/futursolo/sketchbook/actions/workflows/everything.yml/badge.svg
  :target: https://github.com/futursolo/sketchbook/actions/workflows/everything.yml

.. image:: https://coveralls.io/repos/github/futursolo/sketchbook/badge.svg?branch=master
  :target: https://coveralls.io/github/futursolo/sketchbook?branch=master

.. image:: https://img.shields.io/pypi/v/sketchbook
  :target: https://pypi.org/project/sketchbook/

.. image:: https://readthedocs.org/projects/sketchbook/badge/?version=latest
  :target: https://sketchbook.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

A template engine built with async/await syntax support for asyncio and curio.

Intallation
-----------
.. code-block:: shell

    $ pip install -U sketchbook

Source Code
-----------
:code:`sketchbook` is open sourced under
`Apache License 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_ and its
source code is hosted on `GitHub <https://github.com/futursolo/sketchbook/>`_.

Requirements
------------
- Python 3.8.0+
- aiofiles>=0.6,<1(Optional, used by :code:`sketchbook.AsyncSketchFinder`)

Alternative Event Loop
----------------------
Beside the :code:`asyncio` module from the Python standard library, Sketchbook
can also be used with `curio <https://curio.readthedocs.io/en/latest/>`_.

Documentation
-------------
The Documentation is hosted on `Read the Docs <https://sketchbook.readthedocs.io/en/latest/index.html>`_.

License
-------
Copyright 2021 Kaede Hoshikawa

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
