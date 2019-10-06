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

from typing import Callable, Any

import os
import asyncio
import functools
import abc


class BaseTestHelper(abc.ABC):
    def __init__(self, file: str) -> None:
        self._root_path = os.path.dirname(os.path.abspath(file))

    def abspath(self, sub_path: str) -> str:
        return os.path.abspath(
            os.path.realpath(
                os.path.join(self._root_path, sub_path)))

    @abc.abstractmethod
    def force_sync(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        raise NotImplementedError


class AsyncioTestHelper(BaseTestHelper):
    def __init__(self, file: str) -> None:
        self._root_path = os.path.dirname(os.path.abspath(file))

        self._loop = asyncio.get_event_loop()

        self._loop.set_debug(True)

    def force_sync(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(_self: Any, *args: Any, **kwargs: Any) -> Any:
            return self._loop.run_until_complete(
                asyncio.wait_for(
                    fn(_self, *args, **kwargs), 10))

            # Wait 10 sec, or kill the task.

        return wrapper


TestHelper = AsyncioTestHelper

try:
    import curio

except ImportError:
    pass

else:
    class CurioTestHelper(BaseTestHelper):
        def force_sync(self, fn: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(fn)
            def wrapper(_self: Any, *args: Any, **kwargs: Any) -> Any:
                return curio.run(curio.timeout_after(
                        10, fn(_self, *args, **kwargs)))

                # Wait 10 sec, or kill the task.

            return wrapper
