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

from typing import Optional, Union, Dict

from . import context
from . import template
from . import exceptions

import asyncio
import abc
import os
import concurrent.futures
import aiofiles

__all__ = ["BaseLoader", "AsyncFileSystemLoader"]


class BaseLoader(abc.ABC):
    """
    Base Template Loader.

    All Loaders should be a subclass of this class.
    """
    def __init__(
        self, *,
            tpl_ctx: Optional["context.TemplateContext"]=None) -> None:
        self._tpl_ctx = tpl_ctx or context.TemplateContext()
        self._tpl_cache: Dict[str, template.Template] = {}

        self._load_tpl_lock = asyncio.Lock()

    @abc.abstractmethod
    async def _load_tpl_content(
            self, tpl_path: str) -> Union[str, bytes]:  # pragma: no cover
        """
        Load the template content asynchronously.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def _find_abs_path(
        self, tpl_path: str,
            origin_path: Optional[str]=None) -> str:  # pragma: no cover
        """
        Solve the absolute path of the template from the tpl_path based on the
        origin_path(if applicable).

        If no matched file found, it should raise a ``TemplateNotFoundError``.
        """
        raise NotImplementedError

    async def load_tpl(
        self, tpl_path: str,
            origin_path: Optional[str]=None) -> "template.Template":
        """
        Load and parse the template asynchronously.
        """
        async with self._load_tpl_lock:  # Avoid Coroutine Race.
            if tpl_path in self._tpl_cache.keys():
                return self._tpl_cache[tpl_path]

            abs_tpl_path = await self._find_abs_path(
                tpl_path, origin_path=origin_path)

            tpl_content = await self._load_tpl_content(abs_tpl_path)

            tpl = template.Template(
                tpl_content, path=tpl_path, tpl_ctx=self._tpl_ctx, loader=self)

            if self._tpl_ctx.cache_tpls:
                self._tpl_cache[tpl_path] = tpl

            return tpl


class AsyncFileSystemLoader(BaseLoader):
    """
    An implementation of `BaseLoader` loads files from the file system
    asynchronously.
    """
    def __init__(
        self, root_path: str, *,
        executor: Optional[concurrent.futures.ThreadPoolExecutor]=None,
            tpl_ctx: Optional["context.TemplateContext"]=None) -> None:
        assert isinstance(root_path, str)

        self._root_path = os.path.abspath(root_path)
        if not self._root_path.endswith("/"):
            self._root_path += "/"

        super().__init__(tpl_ctx=tpl_ctx)

        self._executor = executor or concurrent.futures.ThreadPoolExecutor()

    @property
    def _loop(self) -> asyncio.AbstractEventLoop:
        return self._tpl_ctx.loop

    async def _find_abs_path(
        self, tpl_path: str,
            origin_path: Optional[str]=None) -> str:
        if origin_path is not None and (not os.path.isabs(tpl_path)):
            origin_dir = os.path.join(
                self._root_path, os.path.dirname(origin_path))

            if not origin_dir.endswith("/"):
                origin_dir += "/"

            if not origin_dir.startswith(self._root_path):
                raise exceptions.TemplateNotFoundError(
                    "To prevent potential directory traversal attack, "
                    "this path is not acceptable.")

        else:
            origin_dir = self._root_path

        if os.path.isabs(tpl_path):
            if tpl_path.find(":") != -1:
                _, tpl_path = tpl_path.split(":", 1)

                if tpl_path[0] in ("/", "\\"):
                    tpl_path = tpl_path[1:]

            else:
                _, tpl_path = tpl_path.split("/", 1)

        final_tpl_path = os.path.join(origin_dir, tpl_path)

        if os.path.exists(final_tpl_path):
            return final_tpl_path

        raise exceptions.TemplateNotFoundError(
            f"No such file {final_tpl_path}.")

    async def _load_tpl_content(self, tpl_path: str) -> bytes:
        async with aiofiles.open(
            tpl_path, mode="rb", executor=self._executor,
                loop=self._loop) as tpl_fp:
            return await tpl_fp.read()
