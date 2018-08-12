Sketchbook
==========
.. image:: https://travis-ci.org/futursolo/sketchbook.svg?branch=master
  :target: https://travis-ci.org/futursolo/sketchbook

.. image:: https://coveralls.io/repos/github/futursolo/sketchbook/badge.svg?branch=master
  :target: https://coveralls.io/github/futursolo/sketchbook?branch=master

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
- Python 3.6+
- aiofiles>=0.3.1,<1(Optional, used by :code:`sketchbook.AsyncSketchFinder`)

Alternative Event Loop
----------------------
Beside the :code:`asyncio` module from the Python standard library, Sketchbook
can also be used with `curio <https://curio.readthedocs.io/en/latest/>`_.

Documentation
-------------
The Documentation is hosted `here <https://sketchbook.futures.moe/>`_.

License
-------
Copyright 2018 Kaede Hoshikawa

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
