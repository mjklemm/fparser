
# All rights reserved.

# Modifications made as part of the fparser project are distributed
# under the following license:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Test C99 Preprocessor directives: This file tests the preprocessor
directives defined in the C99 standard. Whilst this is not part of any
Fortran standard, most compilers support preprocessing of Fortran files
and support the majority of directives from the C-Standard. Since this
is actively used in user codes there are cases where users might like to
keep the directives in the Fortran parse tree and output it again.

'''

import pytest
from fparser.two.C99Preprocessor import (Cpp_Include_Stmt, Cpp_Macro_Stmt,
                                         Cpp_Macro_Identifier, Cpp_Undef_Stmt,
                                         Cpp_Line_Stmt, Cpp_Error_Stmt,
                                         Cpp_Warning_Stmt)
from fparser.two.utils import NoMatchError


def test_include_stmt(f2003_create):
    '''Test that #include is recognized'''
    ref = '#include "filename.inc"'
    code = ['#include "filename.inc"', '   #   include  "filename.inc"  ']
    for line in code:
        result = Cpp_Include_Stmt(line)
        assert str(result) == ref


def test_incorrect_include_stmt(f2003_create):
    '''Test that incorrectly formed #include statements raises exception'''
    code = [None, '', '  ', '#includ', '#includ "x"', '#include',
            '#include ""', "#include 'x'", '#include "x', '#include x"',
            '#include x', '#include x"x"', '#include "x"x', 'x #include "x"',
            '#includex "x"', "#include 'abc'"]
    for line in code:
        with pytest.raises(NoMatchError) as excinfo:
            _ = Cpp_Include_Stmt(line)
        assert "Cpp_Include_Stmt: '{0}'".format(line) in str(excinfo.value)


def test_macro_stmt(f2003_create):
    '''Test that #define is recognized'''
    # definition with value
    ref = '#define MACRO value'
    for line in ['#define MACRO value',
                 '  #  define   MACRO   value  ']:
        result = Cpp_Macro_Stmt(line)
        assert str(result) == ref
    # definition without value
    ref = '#define _MACRO'
    for line in ['#define _MACRO',
                 '   #  define  _MACRO  ']:
        result = Cpp_Macro_Stmt(line)
        assert str(result) == ref
    # more definitions with parameters and similar
    code = ['#define MACRO(x) call func(x)',
            '#define MACRO (x, y)',
            '#define MACRO(x, y) (x) + (y)',
            '#define MACRO(a, b, c, d) (a) * (b) + (c) * (d)',
            '#define eprintf(...) fprintf (stderr, __VA_ARGS__)',
            '#define report(tst, ...) ((tst)?puts(#tst):printf(__VA_ARGS__))',
            '#define hash_hash # ## #',
            '#define TABSIZE 100',
            '#define r(x,y) x ## y',
            '#define MACRO(a, b, c) (a) * (b + c)',
            '#define MACRO( a,b ,   c) (a )*    (   b   + c  )']
    for ref in code:
        result = Cpp_Macro_Stmt(ref)
        assert str(result) == ref


def test_incorrect_macro_stmt(f2003_create):
    '''Test that incorrectly formed #define statements raises exception'''
    for line in [None, '', ' ', '#def', '#defnie', '#definex',
                 '#define fail(...,test) test']:
        with pytest.raises(NoMatchError) as excinfo:
            _ = Cpp_Macro_Stmt(line)
        assert "Cpp_Macro_Stmt: '{0}'".format(line) in str(excinfo.value)


def test_macro_identifier(f2003_create):
    '''Test that all allowed names can be parsed'''
    for name in ['MACRO', 'MACRO1', 'MACRO_', 'macro', '_', '_12']:
        result = Cpp_Macro_Identifier(name)
        assert str(result) == name


def test_undef_stmt(f2003_create):
    '''Test that #undef is recognized'''
    ref = '#undef _MACRO'
    for line in [
        '#undef _MACRO',
        '   #  undef  _MACRO  ',
    ]:
        result = Cpp_Undef_Stmt(line)
        assert str(result) == ref


def test_incorrect_undef_stmt(f2003_create):
    '''Test that incorrectly formed #undef statements raise exception'''
    for line in [None, '', ' ', '#undef', '#unfed', '#undefx']:
        with pytest.raises(NoMatchError) as excinfo:
            _ = Cpp_Undef_Stmt(line)
        assert "Cpp_Undef_Stmt: '{0}'".format(line) in str(excinfo.value)


def test_line_statement(f2003_create):
    '''Test that #line is recognized'''
    ref = '#line CONFIG'
    for line in [
        '#line CONFIG',
        '  #  line   CONFIG  ',
    ]:
        result = Cpp_Line_Stmt(line)
        assert str(result) == ref


def test_incorrect_line_stmt(f2003_create):
    '''Test that incorrectly formed #line statements raise exception'''
    for line in [None, '', ' ', '#line', '#linex', '#lien']:
        with pytest.raises(NoMatchError) as excinfo:
            _ = Cpp_Line_Stmt(line)
        assert "Cpp_Line_Stmt: '{0}'".format(line) in str(excinfo.value)


def test_error_statement(f2003_create):
    '''Test that #error is recognized'''
    # error with message
    ref = '#error MSG'
    for line in [
        '#error MSG',
        '  #  error  MSG  ',
    ]:
        result = Cpp_Error_Stmt(line)
        assert str(result) == ref
    # error without message
    ref = '#error'
    for line in [
        '#error',
        '   #  error  ',
    ]:
        result = Cpp_Error_Stmt(line)
        assert str(result) == ref


def test_incorrect_error_stmt(f2003_create):
    '''Test that incorrectly formed #error statements raise exception'''
    for line in [None, '', ' ', '#erorr', '#errorx']:
        with pytest.raises(NoMatchError) as excinfo:
            _ = Cpp_Error_Stmt(line)
        assert "Cpp_Error_Stmt: '{0}'".format(line) in str(excinfo.value)


def test_warning_statement(f2003_create):
    '''Test that #warning is recognized (not actually part of C99)'''
    # warning with message
    ref = '#warning MSG'
    for line in [
        '#warning MSG',
        '  #  warning  MSG  ',
    ]:
        result = Cpp_Warning_Stmt(line)
        assert str(result) == ref
    # warning without message
    ref = '#warning'
    for line in [
        '#warning',
        '   #  warning  ',
    ]:
        result = Cpp_Warning_Stmt(line)
        assert str(result) == ref


def test_incorrect_warning_stmt(f2003_create):
    '''Test that incorrectly formed #warning statements raise exception'''
    for line in [None, '', ' ', '#wrning', '#warningx']:
        with pytest.raises(NoMatchError) as excinfo:
            _ = Cpp_Warning_Stmt(line)
        assert "Cpp_Warning_Stmt: '{0}'".format(line) in str(excinfo.value)
