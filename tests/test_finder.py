#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2019 Kaede Hoshikawa
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from sketchbook import SketchNotFoundError

import pytest
import os

_TEST_CURIO = True if bool(os.environ.get("TEST_CURIO", False)) else False

if _TEST_CURIO:
    from sketchbook.testutils import CurioTestHelper
    from sketchbook import CurioSketchContext, SyncSketchFinder

    helper = CurioTestHelper(__file__)

    default_skt_ctx = CurioSketchContext()

else:
    from sketchbook.testutils import AsyncioTestHelper
    from sketchbook import AsyncioSketchContext, AsyncSketchFinder, \
        SyncSketchFinder

    helper = AsyncioTestHelper(__file__)

    default_skt_ctx = AsyncioSketchContext()


if not _TEST_CURIO:
    class AsyncSketchFinderTestCase:
        def test_init(self) -> None:
            finder = AsyncSketchFinder(helper.abspath("sketches"))

            assert finder._root_path == helper.abspath("sketches") + "/"

            with pytest.raises(AssertionError):
                AsyncSketchFinder(-1)

        @helper.force_sync
        async def test_find(self) -> None:
            loader = AsyncSketchFinder(helper.abspath("sketches"))

            with pytest.raises(SketchNotFoundError):
                await loader.find("phantasm.html")
            loaded_skt = await loader.find("index.html")

            with open(helper.abspath("sketches/index.html")) as f:
                skt_content = f.read()
            assert loaded_skt._content == skt_content  # Test Correctness.

            sec_loaded_skt = await loader.find("index.html")
            assert loaded_skt is sec_loaded_skt  # Test Sketch Cache.

        @helper.force_sync
        async def test_find_no_cache(self) -> None:
            skt_ctx = AsyncioSketchContext(cache_sketches=False)
            loader = AsyncSketchFinder(
                helper.abspath("sketches"), skt_ctx=skt_ctx)

            loaded_skt = await loader.find("index.html")
            sec_loaded_skt = await loader.find("index.html")

            # Test they have the same content.
            assert loaded_skt._content == sec_loaded_skt._content

            # Test Sketch Cache Disabled.
            assert loaded_skt is not sec_loaded_skt


class InheritanceTestCase:
    @helper.force_sync
    async def test_inherit(self) -> None:
        finder = SyncSketchFinder(
            helper.abspath("sketches"), skt_ctx=default_skt_ctx)

        skt = await finder.find("index.html")

        assert await skt.draw() == """\
<!DOCTYPE HTML>
<html>
    <head>
        <title>Index Title</title>
    </head>
    <body>
        \n
This is body. The old title is Old Title.

    </body>
</html>
"""


class IncludeTestCase:
    @helper.force_sync
    async def test_include(self) -> None:
        finder = SyncSketchFinder(
            helper.abspath("sketches"), skt_ctx=default_skt_ctx)

        skt = await finder.find("main.html")

        assert await skt.draw() == """\
<!DOCTYPE HTML>
<html>
    <head>
        <title>Main Page</title>
    </head>

    <body>

        \n<nav>This will be included in other files.</nav>

    </body>
</html>
"""


class SketchDiscoveryTestCase:
    @helper.force_sync
    async def test_traversal_prevention_for_sync_finder(self) -> None:
        finder = SyncSketchFinder(
            helper.abspath("sketches"), skt_ctx=default_skt_ctx)

        with pytest.raises(SketchNotFoundError):
            await finder._find_abs_path(
                "../hijack.html", helper.abspath("sketches/main.html"))

    if not _TEST_CURIO:
        @helper.force_sync
        async def test_traversal_prevention_for_async_finder(self) -> None:
            finder = AsyncSketchFinder(
                helper.abspath("sketches"), skt_ctx=default_skt_ctx)

            with pytest.raises(SketchNotFoundError):
                await finder._find_abs_path(
                    "../hijack.html", helper.abspath("sketches/main.html"))
