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

from typing import Dict, Any, Optional, Awaitable, Callable, Type, Union, Tuple

from . import sketch
from . import exceptions
from . import finders
from . import context

import abc

__all__ = ["BlockStorage", "BlockRuntime", "SketchRuntime"]


class BlockStorage:
    def __init__(self, skt_rt: "SketchRuntime") -> None:
        self._skt_rt: SketchRuntime
        self._blocks: Dict[str, Type[BlockRuntime]]
        self.__dict__["_skt_rt"] = skt_rt
        self.__dict__["_blocks"] = {}

        self._blocks.update(  # type: ignore
            **self._skt_rt._BLOCK_RUNTIMES)

    def __getitem__(
        self, name: Union[str, Tuple[str, bool]]) -> Callable[
            ..., Awaitable[str]]:
        if isinstance(name, tuple):
            block_name, defined_here = name

        else:
            block_name = name
            defined_here = False

        if block_name not in self._blocks.keys():
            raise KeyError(f"Unknown Block Name {block_name}.")

        SelectedBlockRuntime = self._blocks[block_name]

        async def wrapper() -> str:
            block_rt = SelectedBlockRuntime(  # type: ignore
                self._skt_rt, _defined_here=defined_here)

            await block_rt._draw()

            return block_rt._block_result

        return wrapper

    def __setitem__(self, name: str, value: Any) -> None:  # pragma: no cover
        raise NotImplementedError

    def __getattr__(self, name: str) -> Callable[..., Awaitable[str]]:
        try:
            return self[name]

        except KeyError as e:
            raise AttributeError from e

    __setattr__ = __setitem__

    def _update(self, child_store: "BlockStorage") -> None:
        for k, v in child_store._blocks.items():
            if k not in self._blocks.keys():
                continue

            self._blocks[k] = v


class _BaseRuntime(abc.ABC):
    @property
    @abc.abstractmethod
    def _finder(self) -> "finders.BaseSketchFinder":  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def _get_globals(self) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _ctx(self) -> "context.SketchContext":  # pragma: no cover
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def blocks(self) -> BlockStorage:  # pragma: no cover
        """
        Return an object to access blocks.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def body(self) -> str:  # pragma: no cover
        """
        Return the body from the child.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parent(self) -> "SketchRuntime":  # pragma: no cover
        """
        Return the runtime of the parent(if any).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def write(
        self, __content: Any,
            escape: str="default") -> None:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    async def _inherit_sketch(self) -> None:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    async def _add_parent(self, path: str) -> None:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    async def _include_sketch(self, path: str) -> str:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    async def _draw(self) -> None:  # pragma: no cover
        raise NotImplementedError


class BlockRuntime(_BaseRuntime):
    def __init__(
            self, __skt_rt: "SketchRuntime", _defined_here: bool) -> None:
        self._skt_rt = __skt_rt
        self._defined_here = _defined_here

        self.__skt_result__ = ""

        self._finished = False

    @property
    def _skt(self) -> "sketch.Sketch":
        return self._skt_rt._skt

    @property
    def _finder(self) -> "finders.BaseSketchFinder":
        if self._skt._finder is None:
            raise exceptions.SketchDrawingError(
                "The finder is not set. "
                "The inheritance and including is not available.")
        return self._skt._finder

    def _get_globals(self) -> Dict[str, Any]:
        return self._skt_rt._get_globals()

    @property
    def _ctx(self) -> "context.SketchContext":
        return self._skt_rt._ctx

    @property
    def _block_result(self) -> str:
        if not self._finished:
            raise exceptions.SketchDrawingError(
                "Drawing has not been finished yet.")

        return self.__skt_result__

    @property
    def blocks(self) -> BlockStorage:
        return self._skt_rt.blocks

    def write(self, __content: Any, escape: str="default") -> None:
        if self._finished:
            raise exceptions.SketchDrawingError(
                "Drawing has been finished.")

        self.__skt_result__ += self._ctx.escape_fns[escape](__content)

    @property
    def body(self) -> str:
        return self._skt_rt.body

    @property
    def parent(self) -> "SketchRuntime":
        return self._skt_rt.parent

    async def _inherit_sketch(self) -> None:
        raise exceptions.SketchDrawingError(
            "Cannot inherit sketch(es) inside the block.")

    async def _add_parent(self, path: str) -> None:
        raise exceptions.SketchDrawingError(
            "Cannot Set Inheritance inside the block.")

    async def _include_sketch(self, path: str) -> str:
        return await self._skt_rt._include_sketch(path)

    async def _draw(self) -> None:
        if self._finished:
            raise exceptions.SketchDrawingError(
                "Drawing has already been finished.")

        if self._defined_here and self._skt_rt._parent is not None:
            self._finished = True

            return

        await self._draw_block()

        self._finished = True

    @abc.abstractmethod
    async def _draw_block(self) -> None:  # pragma: no cover
        raise NotImplementedError


class SketchRuntime(_BaseRuntime):
    _BLOCK_RUNTIMES: Dict[str, Type[BlockRuntime]] = {}

    def __init__(
        self, skt: "sketch.Sketch",
            skt_globals: Dict[str, Any]) -> None:
        self._skt = skt
        self._skt_globals = skt_globals

        self.__skt_result__ = ""

        self._body: Optional[str] = None
        self._parent: Optional[SketchRuntime] = None

        self._block_store = BlockStorage(self)

        self._finished = False

    @property
    def _finder(self) -> "finders.BaseSketchFinder":
        if self._skt._finder is None:
            raise exceptions.SketchDrawingError(
                "The finder is not set. "
                "The inheritance and including is not available.")
        return self._skt._finder

    def _get_globals(self) -> Dict[str, Any]:
        new_globals = {}

        new_globals.update(self._skt_globals)

        if "_SktCurrentRuntime" in new_globals.keys():
            del new_globals["_SktCurrentRuntime"]

        return new_globals

    @property
    def _skt_result(self) -> str:
        if not self._finished:
            raise exceptions.SketchDrawingError(
                "Drawing has not been finished yet.")

        return self.__skt_result__

    @property
    def _ctx(self) -> "context.SketchContext":
        return self._skt._ctx

    @property
    def blocks(self) -> BlockStorage:
        return self._block_store

    def write(self, __content: Any, escape: str="default") -> None:
        if self._finished:
            raise exceptions.SketchDrawingError(
                "Drawing has been finished.")

        self.__skt_result__ += self._ctx.escape_fns[escape](__content)

    @property
    def body(self) -> str:
        if self._body is None:
            raise AttributeError("Inheritance is not enabled.")

        return self._body

    @property
    def parent(self) -> "SketchRuntime":
        if self._parent is None:
            raise AttributeError("Parent is not set.")

        return self._parent

    def _update_blocks(self, child_store: BlockStorage) -> None:
        self._block_store._update(child_store)

    def _update_body(self, body: str) -> None:
        assert self._body is None, "There's already a child body."
        self._body = body

    async def _inherit_sketch(self) -> None:
        if self._parent is None:
            return

        self._parent._update_body(self.__skt_result__)
        self._parent._update_blocks(self._block_store)

        await self._parent._draw()

        self.__skt_result__ = self._parent._skt_result

    async def _add_parent(self, path: str) -> None:
        assert self._parent is None, \
            "A sketch can only set the inheritance once."

        parent_skt = await self._finder._find(
            path, origin_path=self._skt._path)

        self._parent = parent_skt._get_runtime(
            skt_globals=self._get_globals())

    async def _include_sketch(self, path: str) -> str:
        skt = await self._finder._find(path, origin_path=self._skt._path)

        skt_rt = skt._get_runtime(self._get_globals())

        await skt_rt._draw()
        return skt_rt._skt_result

    async def _draw(self) -> None:
        if self._finished:
            raise exceptions.SketchDrawingError(
                "Drawing has already been finished.")

        await self._draw_body()

        await self._inherit_sketch()
        self._finished = True

    @abc.abstractmethod
    async def _draw_body(self) -> None:  # pragma: no cover
        raise NotImplementedError
