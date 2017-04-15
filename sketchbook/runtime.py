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

from . import template
from . import exceptions
from . import loaders
from . import context

import abc

__all__ = ["BlockStorage", "BlockNamespace", "TplNamespace"]


class BlockStorage:
    def __init__(self, tpl_namespace: "TplNamespace") -> None:
        self._tpl_namespace: TplNamespace
        self._blocks: Dict[str, Type[BlockNamespace]]
        self.__dict__["_tpl_namespace"] = tpl_namespace
        self.__dict__["_blocks"] = {}

        self._blocks.update(  # type: ignore
            **self._tpl_namespace._BLOCK_NAMESPACES)

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

        SelectedBlockNamespace = self._blocks[block_name]

        async def wrapper() -> str:
            block_namespace = SelectedBlockNamespace(  # type: ignore
                self._tpl_namespace, _defined_here=defined_here)

            await block_namespace._render()

            return block_namespace._block_result

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


class _BaseNamespace(abc.ABC):
    @property
    @abc.abstractmethod
    def _loader(self) -> "loaders.BaseLoader":
        raise NotImplementedError

    @abc.abstractmethod
    def _get_globals(self) -> Dict[str, Any]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def _tpl_ctx(self) -> "context.TemplateContext":
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def blocks(self) -> BlockStorage:
        """
        Return an object to access blocks.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def body(self) -> str:
        """
        Return the body from the child template.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parent(self) -> "TplNamespace":
        """
        Return the namespace of the parent template (if any).
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def _inherit_tpl(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _add_parent(self, path: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _include_tpl(self, path: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def _render(self) -> None:
        raise NotImplementedError


class BlockNamespace(_BaseNamespace):
    def __init__(
            self, tpl_namespace: "TplNamespace", _defined_here: bool) -> None:
        self._tpl_namespace = tpl_namespace
        self._defined_here = _defined_here

        self.__tpl_result__ = ""

        self._finished = False

    @property
    def _tpl(self) -> "template.Template":
        return self._tpl_namespace._tpl

    @property
    def _loader(self) -> "loaders.BaseLoader":
        if self._tpl._loader is None:
            raise exceptions.TemplateRenderError(
                "The loader is not set. "
                "The inheritance and including is not available.")
        return self._tpl._loader

    def _get_globals(self) -> Dict[str, Any]:
        return self._tpl_namespace._get_globals()

    @property
    def _tpl_ctx(self) -> "context.TemplateContext":
        return self._tpl_namespace._tpl_ctx

    @property
    def _block_result(self) -> str:
        if not self._finished:
            raise exceptions.TemplateRenderError(
                "Renderring has not been finished yet.")

        return self.__tpl_result__

    @property
    def blocks(self) -> BlockStorage:
        return self._tpl_namespace.blocks

    @property
    def body(self) -> str:
        return self._tpl_namespace.body

    @property
    def parent(self) -> "TplNamespace":
        return self._tpl_namespace.parent

    async def _inherit_tpl(self) -> None:
        raise exceptions.TemplateRenderError(
            "Cannot inherit template(s) inside the block.")

    async def _add_parent(self, path: str) -> None:
        raise exceptions.TemplateRenderError(
            "Cannot Set Inheritance inside the block.")

    async def _include_tpl(self, path: str) -> str:
        return await self._tpl_namespace._include_tpl(path)

    async def _render(self) -> None:
        if self._finished:
            raise exceptions.TemplateRenderError(
                "Renderring has already been finished.")

        if self._defined_here and self._tpl_namespace._parent is not None:
            self._finished = True

            return

        await self._render_block()

        self._finished = True

    @abc.abstractmethod
    async def _render_block(self) -> None:  # pragma: no cover
        raise NotImplementedError


class TplNamespace(_BaseNamespace):
    _BLOCK_NAMESPACES: Dict[str, Type[BlockNamespace]] = {}

    def __init__(
        self, tpl: "template.Template",
            tpl_globals: Dict[str, Any]) -> None:
        self._tpl = tpl
        self._tpl_globals = tpl_globals

        self.__tpl_result__ = ""

        self._body: Optional[str] = None
        self._parent: Optional[TplNamespace] = None

        self._block_store = BlockStorage(self)

        self._finished = False

    @property
    def _loader(self) -> "loaders.BaseLoader":
        if self._tpl._loader is None:
            raise exceptions.TemplateRenderError(
                "The loader is not set. "
                "The inheritance and including is not available.")
        return self._tpl._loader

    def _get_globals(self) -> Dict[str, Any]:
        new_globals = {}

        new_globals.update(self._tpl_globals)

        if "_TplCurrentNamespace" in new_globals.keys():
            del new_globals["_TplCurrentNamespace"]

        return new_globals

    @property
    def _tpl_result(self) -> str:
        if not self._finished:
            raise exceptions.TemplateRenderError(
                "Renderring has not been finished yet.")

        return self.__tpl_result__

    @property
    def _tpl_ctx(self) -> "context.TemplateContext":
        return self._tpl._tpl_ctx

    @property
    def blocks(self) -> BlockStorage:
        return self._block_store

    @property
    def body(self) -> str:
        if self._body is None:
            raise AttributeError("Inheritance is not enabled.")

        return self._body

    @property
    def parent(self) -> "TplNamespace":
        if self._parent is None:
            raise AttributeError("Parent is not set.")

        return self._parent

    def _update_blocks(self, child_store: BlockStorage) -> None:
        self._block_store._update(child_store)

    def _update_body(self, body: str) -> None:
        assert self._body is None, "There's already a child body."
        self._body = body

    async def _inherit_tpl(self) -> None:
        if self._parent is None:
            return

        self._parent._update_body(self.__tpl_result__)
        self._parent._update_blocks(self._block_store)

        await self._parent._render()

        self.__tpl_result__ = self._parent._tpl_result

    async def _add_parent(self, path: str) -> None:
        assert self._parent is None, \
            "A template can only set the inheritance once."

        parent_tpl = await self._loader.load_tpl(
            path, origin_path=self._tpl._path)

        self._parent = parent_tpl._get_namespace(
            tpl_globals=self._get_globals())

    async def _include_tpl(self, path: str) -> str:
        tpl = await self._loader.load_tpl(path, origin_path=self._tpl._path)

        tpl_namespace = tpl._get_namespace(self._get_globals())

        await tpl_namespace._render()
        return tpl_namespace._tpl_result

    async def _render(self) -> None:
        if self._finished:
            raise exceptions.TemplateRenderError(
                "Renderring has already been finished.")

        await self._render_body()

        await self._inherit_tpl()
        self._finished = True

    @abc.abstractmethod
    async def _render_body(self) -> None:  # pragma: no cover
        raise NotImplementedError
