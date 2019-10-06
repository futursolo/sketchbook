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

from typing import AsyncIterator

from sketchbook import Sketch

import time
import random
import pytest

import os

_TEST_CURIO = True if bool(os.environ.get("TEST_CURIO", False)) else False

if _TEST_CURIO:
    from sketchbook import CurioSketchContext
    from sketchbook.testutils import CurioTestHelper

    import curio

    helper = CurioTestHelper(__file__)

    default_skt_ctx = CurioSketchContext()

else:
    from sketchbook import AsyncioSketchContext
    from sketchbook.testutils import AsyncioTestHelper

    import asyncio

    helper = AsyncioTestHelper(__file__)

    default_skt_ctx = AsyncioSketchContext()


class _AsyncTimeIterator(AsyncIterator[float]):
    def __init__(self) -> None:
        self._time = time.time()

        self._counter_left = random.choice(range(2, 5))

        self._iterated_time = []

    def __aiter__(self) -> "_AsyncTimeIterator":
        return self

    async def __anext__(self) -> float:
        wait_period = random.choice(range(1, 5)) / 100

        if _TEST_CURIO:
            await curio.sleep(wait_period)

        else:
            await asyncio.sleep(wait_period)

        if self._counter_left > 0:
            self._counter_left -= 1

            current_time = time.time()
            self._iterated_time.append(current_time)

            return current_time

        else:
            raise StopAsyncIteration


class IfElifElseTestCase:
    @helper.force_sync
    async def test_if_elif_else(self) -> None:
        skt = Sketch(
            "<% if cond %>cond_str<% elif sub_cond %>sub_cond_str"
            "<% else %>else_str<% end %>", skt_ctx=default_skt_ctx)

        assert await skt.draw(cond=True, sub_cond=True) == "cond_str"

        assert await skt.draw(cond=False, sub_cond=True) == "sub_cond_str"

        assert await skt.draw(cond=False, sub_cond=False) == "else_str"


class AsyncForTestCase:
    @helper.force_sync
    async def test_async_for(self) -> None:
        time_iter = _AsyncTimeIterator()
        skt = Sketch(
            "<% async for i in time_iter %><%r= str(i) %>, <% end %>",
            skt_ctx=default_skt_ctx)

        assert await skt.draw(time_iter=time_iter) == \
            str(time_iter._iterated_time)[1:-1] + ", "


class RaiseErrorTestCase:
    @helper.force_sync
    async def test_raise_error(self):
        skt = Sketch("<% raise RuntimeError %>", skt_ctx=default_skt_ctx)
        with pytest.raises(RuntimeError):
            await skt.draw()


class VariableAssignmentTestCase:
    @helper.force_sync
    async def test_assign_var(self):
        skt = Sketch("<% let a = b %><%= a %>", skt_ctx=default_skt_ctx)

        assert await skt.draw(b="I am b!") == "I am b!"

    @helper.force_sync
    async def test_assign_var_with_extra_equal(self):
        skt = Sketch("<% let a = \"--=--\" %><%= a %>",
                     skt_ctx=default_skt_ctx)

        assert await skt.draw() == "--=--"


class NothingTestCase:
    @helper.force_sync
    async def test_empty_sketch(self) -> None:
        await Sketch("", skt_ctx=default_skt_ctx).draw()
