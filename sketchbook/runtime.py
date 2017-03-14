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

from typing import Dict, Any, Optional

from . import template
from . import exceptions
from . import loaders

import abc

__all__ = ["Namespace"]


class BlockNamespace(abc.ABC):
    def __init__(self, tpl_namespace: "Namespace") -> None:
        self._tpl_namespace = tpl_namespace

        self._tpl = self._tpl_namespace._tpl
        self._tpl_ctx = self._tpl_namespace._tpl_ctx

        self.__tpl_result__ = ""

        self._finished = False

    @property
    def body(self) -> str:
        return self._tpl_namespace.body

    @property
    def parent(self) -> "Namespace":
        return self._tpl_namespace.parent

    @abc.abstractmethod
    async def _render_block(self) -> None:  # pragma: no cover
        raise NotImplementedError

    async def _add_parent(self, path: str) -> None:
        raise exceptions.TemplateRenderError(
            "Cannot Set Inheritance inside the block.")

    @property
    def _block_result(self) -> str:
        if not self._finished:
            raise exceptions.TemplateRenderError(
                "Renderring has not been finished yet.")

        return self.__tpl_result__

    async def _render(self) -> str:
        pass


class Namespace(abc.ABC):
    def __init__(
        self, tpl: "template.Template",
            tpl_globals: Dict[str, Any]) -> None:
        self._tpl = tpl
        self._tpl_ctx = self._tpl._tpl_ctx
        self._tpl_globals = tpl_globals

        self.__tpl_result__ = ""

        self._body: Optional[str] = None
        self._parent: Optional[Namespace] = None

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
    def body(self) -> str:
        """
        Return the body from the child template.
        """
        if self._body is None:
            raise AttributeError("Inheritance is not enabled.")

        return self._body

    @property
    def parent(self) -> "Namespace":
        """
        Return the namespace of the parent template (if any).
        """
        if self._parent is None:
            raise AttributeError("Parent is not set.")

        return self._parent

    def _update_blocks(self, **kwargs: Any) -> None:
        raise NotImplementedError

    def _update_body(self, body: str) -> None:
        assert self._body is None, "There's already a child body."
        self._body = body

    async def _inherit_tpl(self) -> None:
        if self._parent is None:
            return

        self._parent._update_body(self.__tpl_result__)

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

    @abc.abstractmethod
    async def _render_body(self) -> None:  # pragma: no cover
        raise NotImplementedError

    @property
    def _tpl_result(self) -> str:
        if not self._finished:
            raise exceptions.TemplateRenderError(
                "Renderring has not been finished yet.")

        return self.__tpl_result__

    async def _render(self) -> None:
        if self._finished:
            raise exceptions.TemplateRenderError(
                "Renderring has already been finished.")
        await self._render_body()

        await self._inherit_tpl()
        self._finished = True
