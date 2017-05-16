.. _integration:

=======================================
Integrate sketchbook into your projects
=======================================
For simple integration, Only the :class:`.Sketch` class is needed::

    from sketchbook import Sketch

    import asyncio

    async def draw_sketch(name: str) -> str:
        return await Sketch("Hello, <%= name %>.").draw(name=name)

    loop = asyncio.get_event_loop()

    assert loop.run_until_complete(draw_sketch("John Smith")) == "Hello, John Smith."

This is suitable for most simple cases, but you cannot modify behaviours of
sketchbook. Also, it cannot include or inherit from other templates.

Modify Default Behaviours
=========================
To modify the default behaviours of :class:`.Sketch`,
you need to create a :class:`.AsyncioSketchContext` or :class:`CurioSketchContext`.
For example, you want to use a custom event loop for :code:`sketchbook`::

    from sketchbook import Sketch, AsyncioSketchContext

    import uvloop

    loop = uvloop.Loop()
    # This is not the recommended way to use uvloop,
    # please refer to their documentation to set the event loop policy.

    skt_ctx = AsyncioSketchContent(loop=loop)

    async def draw_sketch(name: str) -> str:
        return await Sketch("Hello, <%= name %>.", skt_ctx=skt_ctx).draw(name=name)

    assert loop.run_until_complete(draw_sketch("John Smith")) == "Hello, John Smith."

Inheritance and Including
=========================
To enable the including and inheritance, you need a sketch finder to
help sketches find the other sketches. You can use the finders provided by :code:`sketchbook`
or write your own from :class:`.BaseSketchFinder`.

Let's say that you have a directory called :code:`sketches` and a program known
as :code:`draw.py` field body with the following layout:

.. code-block:: text

    /
      draw.py
      sketches/
        home.html
        header.html
        footer.html
        layout.html

In the files above, :code:`home.html` inherits from :code:`layout.html`, and
:code:`layout.html` includes :code:`header.html` and :code:`footer.html`.
Your program :code:`draw.py` is under the main directory(:code:`/`).

You can put the following code into your :code:`draw.py`::

    from sketchbook import SyncSketchFinder

    import asyncio

    skt_finder = SyncSketchFinder("sketches")

    async def draw_sketch() -> str:
        home_skt = await skt_finder.find("home.html")

        return await home_skt.draw()

    loop = asyncio.get_event_loop()

    print(loop.run_until_complete(draw_sketch()))

Sketch contexts also works for :class:`.BaseSketchFinder`::

    from sketchbook import AsyncSketchFinder, AsyncioSketchContext

    skt_ctx = AsyncioSketchContext(cache_sketches=False)
    # You can disable sketch cache in development.

    skt_finder = AsyncSketchFinder("sketches", skt_ctx=skt_ctx)

Use concurrent I/O as the concurrent library
============================================
If you want to use `concurrent I/O <https://curio.readthedocs.io/>`_ as the
asynchronous library in your project, you need to create your sketches or finders
with :class:`.CurioSketchContext` or it will still use :code:`asyncio` internally.

.. code-block:: python3

    from sketchbook import CurioSketchContext, Sketch

    import curio

    sketch = Sketch("Hello, <%= await name %>!", skt_ctx=CurioSketchContext())

    assert curio.run(sketch.draw(name="John Smith")) == "Hello, John Smith!"
