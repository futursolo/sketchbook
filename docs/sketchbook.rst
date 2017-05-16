.. _sketchbook:

=============
API Reference
=============

Sketch
======
.. autoclass:: sketchbook.Sketch
   :members:
   :undoc-members:

Contexts
========
.. autoclass:: sketchbook.BaseSketchContext

.. autoclass:: sketchbook.AsyncioSketchContext
    :members:

.. autoclass:: sketchbook.CurioSketchContext
    :members:

.. class:: sketchbook.SketchContext

    .. deprecated:: 0.2.0

        Use :class:`.AsyncioSketchContext` instead.

    A Deprecated alias of :class:`.AsyncioSketchContext`

Finders
=======
.. autoclass:: sketchbook.BaseSketchFinder
    :members:
    :special-members:
    :private-members:

.. autoclass:: sketchbook.AsyncSketchFinder
    :members:
    :undoc-members:

.. autoclass:: sketchbook.SyncSketchFinder
    :members:
    :undoc-members:

.. class:: sketchbook.SketchFinder

    .. deprecated:: 0.2.0

        Use :class:`.AsyncSketchFinder` instead.

    A Deprecated alias of :class:`.AsyncSketchFinder`

Runtime
=======
.. autoclass:: sketchbook.SketchRuntime
    :members:
    :undoc-members:

.. autoclass:: sketchbook.BlockStorage

.. autoclass:: sketchbook.BlockRuntime

Exceptions
==========
.. autoclass:: sketchbook.SketchbookException
    :members:
    :undoc-members:

.. autoclass:: sketchbook.SketchSyntaxError
    :members:
    :undoc-members:

.. autoclass:: sketchbook.UnknownStatementError
    :members:
    :undoc-members:

.. autoclass:: sketchbook.SketchNotFoundError
    :members:
    :undoc-members:

.. autoclass:: sketchbook.BlockNameConflictError
    :members:
    :undoc-members:

.. autoclass:: sketchbook.SketchDrawingError
    :members:
    :undoc-members:
