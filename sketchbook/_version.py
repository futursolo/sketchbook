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

import typing

if typing.TYPE_CHECKING:  # pragma: no cover
    import importlib.metadata as importlib_metadata

else:
    try:
        import importlib.metadata as importlib_metadata

    except ImportError:
        import importlib_metadata

__version__ = importlib_metadata.version(__name__.split(".", 1)[0])

__all__ = ["__version__"]
