master
======
- Switch from setuptools to Poetry
- Update Dependencies
- Switch from Travis CI to GitHub Actions
- Update minimum Python version to be 3.8
- :code:`loop` parameter in :code:`AsyncioSketchContext` has no effect now.
- Sketchbook is now compatible with `asyncio.run`
- Docs are now hosted on readthedocs.

v0.2.1
======
- Update Automated version system
- Fix a bug in variable assignment statement when right hand contains `=`
- Update Documentation

v0.2.0
======
- Support concurrent I/O
- Add SyncSketchFinder
- Rename SketchFinder to AsyncSketchFinder
- Rename SketchContext to AsyncioSketchContext
- Deprecate SketchFinder and SketchContext
- Expose sketch context in the runtime
- Fix a code generation problem when the sketch is empty

v0.1.1
======
- Fix :code:`setup.py` Information

v0.1.0
======
- Initial Release
