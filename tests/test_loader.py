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

from sketchbook import AsyncFileSystemLoader, TemplateContext, \
    TemplateNotFoundError
from sketchbook.testutils import TestHelper

import pytest

helper = TestHelper(__file__)


class AsyncFileSystemLoaderTestCase:
    def test_init(self) -> None:
        loader = AsyncFileSystemLoader(helper.abspath("tpls"))

        assert loader._root_path == helper.abspath("tpls") + "/"

        with pytest.raises(AssertionError):
            AsyncFileSystemLoader(-1)

    @helper.force_sync
    async def test_load_tpl(self) -> None:
        loader = AsyncFileSystemLoader(helper.abspath("tpls"))

        with pytest.raises(TemplateNotFoundError):
            await loader.load_tpl("phantasm.html")
        loaded_tpl = await loader.load_tpl("index.html")

        with open(helper.abspath("tpls/index.html")) as f:
            tpl_content = f.read()
        assert loaded_tpl._tpl_content == tpl_content  # Test Correctness.

        sec_loaded_tpl = await loader.load_tpl("index.html")
        assert loaded_tpl is sec_loaded_tpl  # Test Template Cache.

    @helper.force_sync
    async def test_load_tpl_no_cache(self) -> None:
        tpl_ctx = TemplateContext(cache_tpls=False)
        loader = AsyncFileSystemLoader(helper.abspath("tpls"), tpl_ctx=tpl_ctx)

        loaded_tpl = await loader.load_tpl("index.html")
        sec_loaded_tpl = await loader.load_tpl("index.html")

        # Test they have the same content.
        assert loaded_tpl._tpl_content == sec_loaded_tpl._tpl_content

        # Test Template Cache Disabled.
        assert loaded_tpl is not sec_loaded_tpl


class InheritanceTestCase:
    @helper.force_sync
    async def test_inherit(self) -> None:
        loader = AsyncFileSystemLoader(helper.abspath("tpls"))

        tpl = await loader.load_tpl("index.html")

        assert await tpl.render() == """\
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
        loader = AsyncFileSystemLoader(helper.abspath("tpls"))

        tpl = await loader.load_tpl("main.html")

        assert await tpl.render() == """\
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
