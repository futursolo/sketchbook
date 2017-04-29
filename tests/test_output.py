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

from sketchbook import Sketch, SketchContext
from sketchbook.testutils import TestHelper

helper = TestHelper(__file__)


class OutputTestCase:
    @helper.force_sync
    async def test_html_escape(self) -> None:
        skt = Sketch("Hello, <%html= a %>!")

        assert await skt.draw(a="<h1>world</h1>") == \
            "Hello, &lt;h1&gt;world&lt;/h1&gt;!"

    @helper.force_sync
    async def test_no_escape(self) -> None:
        skt = Sketch("Hello, <%r= a %>!")

        assert await skt.draw(a="<h1>world</h1>") == "Hello, <h1>world</h1>!"

    @helper.force_sync
    async def test_json_escape(self) -> None:
        skt = Sketch('{"name": <%json= name %>}')

        assert await skt.draw(name="{\"name\": \"admin\"}") == \
            '{\"name\": \"{\\"name\\": \\"admin\\"}\"}'

    @helper.force_sync
    async def test_url_escape(self) -> None:
        skt = Sketch("https://www.example.com/?user=<%u= name %>")
        assert await skt.draw(name="a&redirect=https://www.example2.com/") == \
            ("https://www.example.com/?user=a%26redirect%3Dhttps%3A%2F%2F"
             "www.example2.com%2F")

    @helper.force_sync
    async def test_url_without_plus_escape(self) -> None:
        skt = Sketch("https://www.example.com/?user=<%url_without_plus= name %>")
        assert await skt.draw(name="John Smith") == \
            "https://www.example.com/?user=John%20Smith"


    @helper.force_sync
    async def test_custom_escape_fn(self) -> None:
        def _number_fn(i: int) -> str:
            return str(i + 1)

        skt_ctx = SketchContext(custom_escape_fns={"number": _number_fn})
        skt = Sketch("The result is <% number= a %>.", skt_ctx=skt_ctx)

        assert await skt.draw(a=12345) == "The result is 12346."
