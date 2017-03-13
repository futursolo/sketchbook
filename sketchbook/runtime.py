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

import abc

__all__ = ["Namespace"]


class Namespace(abc.ABC):
    def __init__(
        self, tpl: "template.Template",
            tpl_globals: Dict[str, Any]) -> None:
        self._tpl = tpl
        self._tpl_ctx = self._tpl._tpl_ctx
        self._tpl_globals = tpl_globals

        self._tpl_result = ""

        self._body: Optional[str] = None

    @property
    def body(self) -> str:
        raise NotImplementedError

    @property
    def parent(self) -> "Namespace":
        raise NotImplementedError

    def _update_blocks(self, **kwargs: Any) -> None:
        raise NotImplementedError

    def _update_body(self, body: str) -> None:
        raise NotImplementedError

    async def _inherit_tpl(self) -> None:
        raise NotImplementedError

    async def _add_parent(self, path: str) -> None:
        raise NotImplementedError

    async def _include_tpl(self, path: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def _render_body_str(self) -> str:  # pragma: no cover
        raise NotImplementedError

    @property
    def _tpl_result(self) -> str:
        return self._tpl_result

    async def _render(self) -> str:
        raise NotImplementedError
