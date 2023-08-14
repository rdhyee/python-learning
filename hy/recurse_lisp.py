# https://www.recurse.com/pairing-tasks

"""
Raymond Yee's solution to the Recurse Center's Pairing Task on Lisp syntax 
parsing and evaluation
2023.08.13

Limitations:
- handles whitespaces (as defined by str.split()) as token separators and ( 
    and ) as reserved characters. 
- does not handle strings, floats, or other data types -- only integers among 
    numeric types
"""

import pytest

# first pass: deal with only spaces, ( and ) as reserved characters for
# tokenizing a string


def raw_tokenize(s: str) -> list:
    # replace ( and ) with surrounding spaces
    s = s.replace("(", " ( ").replace(")", " ) ")
    return s.split()


def to_int(s: str) -> int or str:
    # convert a string to an int if possible
    try:
        return int(s)
    except ValueError:
        return s


def typify_token(s: str) -> int or str:
    """
    for now, convert the token to an int if possible, otherwise leave token as
    a string
    """
    return to_int(s)


def tokenize(s: str) -> list:
    return [typify_token(t) for t in raw_tokenize(s)]


def ast_from_tokens(tokens: list) -> list:
    stack = []

    for i, token in enumerate(tokens):
        if token == "(":
            stack.append([])
        elif token == ")":
            try:
                top = stack.pop()
            except Exception:
                raise ParseError("Closing ) without corresponding (")
            else:
                if len(stack) > 0:
                    stack[-1].append(top)
                else:
                    # successful completion if this is the last token
                    if i + 1 == len(tokens):
                        return top
                    else:
                        raise ParseError("Extra tokens beyond valid expression")

        else:
            try:
                stack[-1].append(token)
            except Exception:
                raise ParseError("Missing opening (")

    if len(stack) > 0:
        raise ParseError("Missing closing )")


class ParseError(Exception):
    pass


TEST_INPUT = "(first (list 1 (+ 2 3) 9))"
TEST_OUTPUT = ["first", ["list", 1, ["+", 2, 3], 9]]


class TestParseError:
    def test_given_testcase(self):
        assert ast_from_tokens(tokenize(TEST_INPUT)) == TEST_OUTPUT

    def test_missing_start_paren(self):
        # detect that the error message is correct
        with pytest.raises(ParseError) as excinfo:
            ast_from_tokens(tokenize("first list 1 (+ 2 3) 9)"))
        assert "Missing opening (" in str(excinfo.value)

    def test_missing_end_paren(self):
        with pytest.raises(ParseError) as excinfo:
            ast_from_tokens(tokenize("(first list 1 (+ 2 3) 9"))
        assert "Missing closing )" in str(excinfo.value)

    def test_extra_tokens(self):
        with pytest.raises(ParseError) as excinfo:
            ast_from_tokens(tokenize("(first list 1 (+ 2 3) 9) extra"))
        assert "Extra tokens beyond valid expression" in str(excinfo.value)

    def test_closing_paren_without_opening(self):
        with pytest.raises(ParseError) as excinfo:
            ast_from_tokens(tokenize(")"))
        assert "Closing ) without corresponding (" in str(excinfo.value)
