#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Copyright 2021 Kaede Hoshikawa
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

from typing import Any

from . import _version, context, exceptions, finders, runtime, sketch
from ._version import *  # noqa: F403
from .context import *  # noqa: F403
from .exceptions import *  # noqa: F403
from .finders import *  # noqa: F403
from .runtime import *  # noqa: F403
from .sketch import *  # noqa: F403
from .utils import deprecated_attr

SketchContext = deprecated_attr(
    AsyncioSketchContext,  # noqa: F405
    __name__,
    "`SketchContext` is deprecated, use `AsyncioSketchContext` instead.",
)

try:
    from .finders import AsyncSketchFinder as _SketchFinder

except ImportError:

    class _SketchFinder:  # type: ignore  # noqa: SIM119
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError(
                "Aiofiles is not installed. "
                "Please install aiofiles before using AsyncSketchFinder."
            )


SketchFinder = deprecated_attr(
    _SketchFinder,
    __name__,
    "`SketchFinder` is deprecated, use `AsyncSketchFinder` instead.",
)

__all__ = (
    _version.__all__
    + context.__all__
    + exceptions.__all__
    + finders.__all__
    + runtime.__all__
    + sketch.__all__
    + ["SketchFinder", "SketchContext"]
)
