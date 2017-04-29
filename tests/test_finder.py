#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2017 Kaede Hoshikawa
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

from sketchbook import SketchFinder, SketchContext, \
    SketchNotFoundError
from sketchbook.testutils import TestHelper

import pytest

helper = TestHelper(__file__)


class SketchFinderTestCase:
    def test_init(self) -> None:
        finder = SketchFinder(helper.abspath("sketches"))

        assert finder._root_path == helper.abspath("sketches") + "/"

        with pytest.raises(AssertionError):
            SketchFinder(-1)

    @helper.force_sync
    async def test_find(self) -> None:
        loader = SketchFinder(helper.abspath("sketches"))

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
        skt_ctx = SketchContext(cache_sketches=False)
        loader = SketchFinder(helper.abspath("sketches"), skt_ctx=skt_ctx)

        loaded_skt = await loader.find("index.html")
        sec_loaded_skt = await loader.find("index.html")

        # Test they have the same content.
        assert loaded_skt._content == sec_loaded_skt._content

        # Test Sketch Cache Disabled.
        assert loaded_skt is not sec_loaded_skt


class InheritanceTestCase:
    @helper.force_sync
    async def test_inherit(self) -> None:
        finder = SketchFinder(helper.abspath("sketches"))

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
        finder = SketchFinder(helper.abspath("sketches"))

        skt = await finder.find("main.html")

        assert await skt.draw() == """\
<!DOCTYPE HTML>
<html>
    <head>
        <title>Main Page</title>
    </head>

    <body>

        \n<nav>This will be included into other files.</nav>

    </body>
</html>
"""


class SketchDiscoveryTestCase:
    @helper.force_sync
    async def test_traversal_prevention(self) -> None:
        finder = SketchFinder(helper.abspath("sketches"))

        with pytest.raises(SketchNotFoundError):
            await finder._find_abs_path(
                "../hijack.html", helper.abspath("sketches/main.html"))
