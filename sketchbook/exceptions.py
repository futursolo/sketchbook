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

__all__ = [
    "SketchbookException", "SketchNotFoundError", "SketchSyntaxError",
    "UnknownStatementError", "BlockNameConflictError", "SketchDrawingError"]


class SketchbookException(Exception):
    """
    Base class of exceptions from Sketchbook.
    """
    pass


class SketchNotFoundError(FileNotFoundError, SketchbookException):
    """
    Error when trying to load a sketch but the finder cannot find it.
    """
    pass


class SketchSyntaxError(SyntaxError, SketchbookException):
    """
    Syntax error in the current sketch.
    """
    pass


class UnknownStatementError(SketchSyntaxError):
    """
    The statement string is not a valid statement.
    """
    pass


class BlockNameConflictError(SketchbookException):
    """
    There's more than one block with the same name in one sketch.
    """
    pass


class SketchDrawingError(SketchbookException):
    """
    Error when drawing the sketch.
    """
    pass
