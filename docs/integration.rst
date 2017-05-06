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

Alter Default Behaviours
========================
To alter the default behaviours of :class:`.Sketch`,
you need to create a :class:`.SketchContext`.
For example, you want to use a custom event loop for :code:`sketchbook`::

    from sketchbook import Sketch, SketchContext

    import uvloop

    loop = uvloop.Loop()
    # This is not the recommended way to use uvloop,
    # please refer to their documentation to set the event loop policy.

    skt_ctx = SketchContent(loop=loop)

    async def draw_sketch(name: str) -> str:
        return await Sketch("Hello, <%= name %>.", skt_ctx=skt_ctx).draw(name=name)

    assert loop.run_until_complete(draw_sketch("John Smith")) == "Hello, John Smith."

Inheritance and Including
=========================
To enable the including and inheritance, you need a :class:`.SketchFinder` to
help sketches find the other sketches. You can use the one provided by :code:`sketchbook`
which delegates the file system operations to `aiofiles <https://github.com/Tinche/aiofiles>`_
to load sketches from your local disk asynchronously, or write your own from
:class:`.BaseSketchFinder`.

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

    from sketchbook import SketchFinder

    import asyncio

    skt_finder = SketchFinder("sketches")

    async def draw_sketch() -> str:
        home_skt = await skt_finder.find("home.html")

        return await home_skt.draw()

    loop = asyncio.get_event_loop()

    print(loop.run_until_complete(draw_sketch()))

Absolutely, :class:`.SketchContext` also works for :class:`.SketchFinder`::

    from sketchbook import SketchFinder, SketchContext

    skt_ctx = SketchContext(cache_sketches=False)
    # You can disable sketch cache in development.

    skt_finder = SketchFinder("sketches", skt_ctx=skt_ctx)

