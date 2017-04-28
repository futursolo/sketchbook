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

from sketchbook import Template, TemplateSyntaxError, UnknownStatementError
from sketchbook.testutils import TestHelper

import pytest

helper = TestHelper(__file__)

class StatementEscapeTestCase:
    @helper.force_sync
    async def test_stmts_escape(self) -> None:
        tpl = Template(
            "<%% is the begin mark, and <%r= \"%%> is the end mark. \" %>"
            "<%r= \"<% and\" %> %> only need to be escaped whenever they "
            "have ambiguity of the templating system.")

        assert await tpl.render() == (
            "<% is the begin mark, and %> is the end mark. "
            "<% and %> only need to be escaped whenever they "
            "have ambiguity of the templating system.")

    @helper.force_sync
    async def test_multiline_stmts(self) -> None:
        tpl = Template("""\
<% if a == \
            True
%>
Hello, it's me!
<% else %>
No, it's not me!
<% end %>""")

        assert await tpl.render(a=True) == "\nHello, it's me!\n"
        assert await tpl.render(a=False) == "\nNo, it's not me!\n"


class MalformedTemplateTestCase:
    def test_malformed_stmts(self) -> None:
        with pytest.raises(TemplateSyntaxError):
            Template("<% <%")

    def test_missing_end_mark(self) -> None:
        with pytest.raises(TemplateSyntaxError):
            Template("<% while True %>")

    def test_redundant_end_mark(self) -> None:
        with pytest.raises(TemplateSyntaxError):
            Template("<% if False %><% end %><% end %>")

    def test_unknown_stmt(self) -> None:
        with pytest.raises(UnknownStatementError):
            Template("<% if anyways %><% fi %>")

    def test_bad_assignment(self) -> None:
        with pytest.raises(TemplateSyntaxError):
            Template("<% let a = b = c = d %>")
