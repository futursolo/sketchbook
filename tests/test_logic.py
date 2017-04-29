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

from typing import AsyncIterator

from sketchbook import Sketch
from sketchbook.testutils import TestHelper

helper = TestHelper(__file__)

import time
import random
import asyncio
import pytest


class _AsyncTimeIterator(AsyncIterator[float]):
    def __init__(self) -> None:
        self._time = time.time()

        self._counter_left = random.choice(range(2, 5))

        self._iterated_time = []

    def __aiter__(self) -> "_AsyncTimeIterator":
        return self

    async def __anext__(self) -> float:
        await asyncio.sleep(random.choice(range(1, 5)) / 100)

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
            "<% else %>else_str<% end %>")

        assert await skt.draw(cond=True, sub_cond=True) == "cond_str"

        assert await skt.draw(cond=False, sub_cond=True) == "sub_cond_str"

        assert await skt.draw(cond=False, sub_cond=False) == "else_str"


class AsyncForTestCase:
    @helper.force_sync
    async def test_async_for(self) -> None:
        time_iter = _AsyncTimeIterator()
        skt = Sketch(
            "<% async for i in time_iter %><%r= str(i) %>, <% end %>")

        assert await skt.draw(time_iter=time_iter) == \
            str(time_iter._iterated_time)[1:-1] + ", "


class RaiseErrorTestCase:
    @helper.force_sync
    async def test_raise_error(self):
        skt = Sketch("<% raise RuntimeError %>")
        with pytest.raises(RuntimeError):
            await skt.draw()

class VariableAssignmentTestCase:
    @helper.force_sync
    async def test_assign_var(self):
        skt = Sketch("<% let a = b %><%= a %>")

        assert await skt.draw(b="I am b!") == "I am b!"
