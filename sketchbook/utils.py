#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   copyright 2019 kaede hoshikawa
#
#   licensed under the apache license, version 2.0 (the "license");
#   you may not use this file except in compliance with the license.
#   you may obtain a copy of the license at
#
#       http://www.apache.org/licenses/license-2.0
#
#   unless required by applicable law or agreed to in writing, software
#   distributed under the license is distributed on an "as is" basis,
#   without warranties or conditions of any kind, either express or implied.
#   see the license for the specific language governing permissions and
#   limitations under the license.

from typing import List, Any
from types import ModuleType

import sys
import warnings


class _DeprecatedAttr:
    def __init__(self, attr: Any, message: str) -> None:
        self._attr = attr
        self._message = message

    def get_attr(self) -> Any:
        warnings.warn(self._message, DeprecationWarning)
        return self._attr


class _ModWithDeprecatedAttrs:
    def __init__(self, mod: ModuleType) -> None:
        self.__dict__["__module__"] = mod

    def __getattr__(self, name: str) -> Any:
        mod_attr = getattr(self.__module__, name)

        if isinstance(mod_attr, _DeprecatedAttr):
            return mod_attr.get_attr()

        return mod_attr

    def __setattr__(self, name: str, attr: Any) -> None:
        return setattr(self.__module__, name, attr)

    def __dir__(self) -> List[str]:
        return dir(self.__module__)


def deprecated_attr(
        attr: Any, mod_name: str, message: str) -> _DeprecatedAttr:
    """
    Mark an attribute as deprecated in a module.
    """
    mod = sys.modules[mod_name]

    if not isinstance(mod, _ModWithDeprecatedAttrs):
        sys.modules[mod_name] = _ModWithDeprecatedAttrs(mod)  # type: ignore

    return _DeprecatedAttr(attr, message)
