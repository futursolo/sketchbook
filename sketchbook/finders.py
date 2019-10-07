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

from typing import Optional, Union, Dict

from . import context
from . import sketch
from . import exceptions

import asyncio
import abc
import os
import concurrent.futures

try:
    import curio

except ImportError:
    pass

__all__ = ["BaseSketchFinder", "SyncSketchFinder"]


class BaseSketchFinder(abc.ABC):
    """
    Base Sketch Finder.

    To create a custom sketch finder, subclass this class and override
    corresponding methods.

    :arg skt_ctx: The :class:`.AsyncioSketchContext` to be used by the
        :class:`.BaseSketchFinder` and :class:`.Sketch`. Default: :code:`None`
        (Create a new :class:`.AsyncioSketchContext` upon initialization).
    """
    def __init__(
        self, *,
            skt_ctx: Optional["context.BaseSketchContext"] = None) -> None:
        self._ctx = skt_ctx or context.AsyncioSketchContext()
        self._skt_cache: Dict[str, sketch.Sketch] = {}

        if isinstance(self._ctx, context.AsyncioSketchContext):
            self._find_skt_lock = asyncio.Lock()

        elif isinstance(self._ctx, context.CurioSketchContext):
            self._find_skt_lock = curio.Lock()

        else:
            raise RuntimeError("Unknown sketch context.")

    @abc.abstractmethod
    async def _load_sketch_content(
            self, skt_path: str) -> Union[str, bytes]:  # pragma: no cover
        """
        This is an :func:`abc.abstractmethod`.

        Override this method to customize sketch loading.

        Load the sketch content as string or bytestring.

        .. important::

            If no matched sketch can be found, it should raise a
            :class:`.SketchNotFoundError`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def _find_abs_path(
        self, skt_path: str,
            origin_path: Optional[str] = None) -> str:  # pragma: no cover
        """
        This is an :func:`abc.abstractmethod`.

        Override this method to customize sketch discovery.

        Solve the absolute path(starting with :code:`/`) of the sketch from
        :code:`skt_path` based on the :code:`origin_path` (if applicable).

        .. important::

            If no matched file is found, it should raise a
            :class:`.SketchNotFoundError`.
        """
        raise NotImplementedError

    async def _find(
        self, skt_path: str,
            origin_path: Optional[str] = None) -> "sketch.Sketch":
        async with self._find_skt_lock:  # Find one sketch at a time.
            if skt_path in self._skt_cache.keys():
                # Try to read from the cache.
                return self._skt_cache[skt_path]

            # Resolve the path.
            abs_skt_path = await self._find_abs_path(
                skt_path, origin_path=origin_path)

            skt_content = await self._load_sketch_content(abs_skt_path)

            skt = sketch.Sketch(
                skt_content, path=skt_path, skt_ctx=self._ctx,
                finder=self)

            if self._ctx.cache_sketches:
                self._skt_cache[skt_path] = skt

            return skt

    async def find(self, skt_path: str) -> "sketch.Sketch":
        """
        Find the sketch corresponding to the given :code:`skt_path` and
        initialize them with :code:`skt_ctx`.

        .. warning::

            If no sketch is matched, this method will raise a
            :class:`.SketchNotFoundError`.
        """
        return await self._find(skt_path)


class SyncSketchFinder(BaseSketchFinder):
    """
    An implementation of :class:`BaseSketchFinder` using the synchronous
    file system operations from standard library.

    :arg __root_path: The root path of the finder. Use :code:`/` in
        inclusion and inheritance to indicate the root path. This argument
        must be passed positionally and must be the first argument.
    :arg skt_ctx: The :class:`.BaseSketchContext` to be used by the
        :class:`.SyncSketchFinder` and :class:`.Sketch`.
        Default: :code:`None` (Create a new :class:`.AsyncioSketchContext`
        upon initialization).
    """
    def __init__(
        self, __root_path: str, *,
        executor: Optional[concurrent.futures.ThreadPoolExecutor] = None,
        skt_ctx: Optional[
            "context.BaseSketchContext"] = None) -> None:
        assert isinstance(__root_path, str)

        super().__init__(skt_ctx=skt_ctx)

        self._root_path = os.path.abspath(__root_path)
        if not self._root_path.endswith("/"):
            self._root_path += "/"

    async def _find_abs_path(
        self, skt_path: str,
            origin_path: Optional[str] = None) -> str:
        skt_path = skt_path.replace("\\", "/")
        # Replace Windows Style Path to UNIX Style.

        if origin_path is not None and (not os.path.isabs(skt_path)):
            origin_dir = os.path.join(
                self._root_path, os.path.dirname(origin_path))

        else:
            origin_dir = self._root_path

        if os.path.isabs(skt_path):
            _, skt_path = skt_path.split("/", 1)
            # Take out the root identifier.

        final_skt_path = os.path.abspath(
            os.path.join(origin_dir, skt_path))
        final_skt_dir = os.path.dirname(final_skt_path)

        if not final_skt_dir.endswith("/"):
            final_skt_dir += "/"

        if not final_skt_path.startswith(self._root_path):
            raise exceptions.SketchNotFoundError(
                "To prevent potential directory traversal attack, "
                "this path is not acceptable.")

        if not os.path.exists(final_skt_path):
            raise exceptions.SketchNotFoundError(
                f"No such file {final_skt_path}.")

        return final_skt_path

    async def _load_sketch_content(self, skt_path: str) -> bytes:
        with open(skt_path, mode="rb") as skt_fp:
            return skt_fp.read()


try:
    import aiofiles

except ImportError:  # pragma: no cover
    pass

else:
    class AsyncSketchFinder(BaseSketchFinder):
        """
        An implementation of :class:`.BaseSketchFinder` using
        `aiofiles <https://github.com/Tinche/aiofiles>`_ to
        load sketches from the local file system asynchronously.

        .. important::

            This finder must be used with an asyncio event loop.

        :arg __root_path: The root path of the finder. Use :code:`/` in
            inclusion and inheritance to indicate the root path. This argument
            must be passed positionally and must be the first argument.
        :arg executor: The executor used by :code:`aiofiles` to load files.
            Default: :code:`None` (Create a new executor upon initialization).
        :arg skt_ctx: The :class:`.AsyncioSketchContext` to be used by the
            :class:`.AsyncSketchFinder` and :class:`.Sketch`.
            Default: :code:`None` (Create a new :class:`.AsyncioSketchContext`
            upon initialization).

        """
        def __init__(
            self, __root_path: str, *,
            executor: Optional[concurrent.futures.ThreadPoolExecutor] = None,
            skt_ctx: Optional[
                "context.AsyncioSketchContext"] = None) -> None:
            assert isinstance(__root_path, str)

            super().__init__(skt_ctx=skt_ctx)

            if not isinstance(self._ctx, context.AsyncioSketchContext):
                raise RuntimeError(
                    "AsyncSketchFinder can only be used with "
                    "AsyncioSketchContext.")

            self._root_path = os.path.abspath(__root_path)
            if not self._root_path.endswith("/"):
                self._root_path += "/"

            self._executor = \
                executor or concurrent.futures.ThreadPoolExecutor()

        @property
        def _loop(self) -> asyncio.AbstractEventLoop:
            assert isinstance(self._ctx, context.AsyncioSketchContext)

            return self._ctx.loop

        async def _find_abs_path(
            self, skt_path: str,
                origin_path: Optional[str] = None) -> str:
            skt_path = skt_path.replace("\\", "/")
            # Replace Windows Style Path to UNIX Style.

            if origin_path is not None and (not os.path.isabs(skt_path)):
                origin_dir = os.path.join(
                    self._root_path, os.path.dirname(origin_path))

            else:
                origin_dir = self._root_path

            if os.path.isabs(skt_path):
                _, skt_path = skt_path.split("/", 1)
                # Take out the root identifier.

            final_skt_path = os.path.abspath(
                os.path.join(origin_dir, skt_path))
            final_skt_dir = os.path.dirname(final_skt_path)

            if not final_skt_dir.endswith("/"):
                final_skt_dir += "/"

            if not final_skt_path.startswith(self._root_path):
                raise exceptions.SketchNotFoundError(
                    "To prevent potential directory traversal attack, "
                    "this path is not acceptable.")

            if not os.path.exists(final_skt_path):
                raise exceptions.SketchNotFoundError(
                    f"No such file {final_skt_path}.")

            return final_skt_path

        async def _load_sketch_content(self, skt_path: str) -> bytes:
            async with aiofiles.open(
                skt_path, mode="rb", executor=self._executor,
                    loop=self._loop) as skt_fp:
                return await skt_fp.read()

    __all__.append("AsyncSketchFinder")
